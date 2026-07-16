import os
import json
import yaml
import logging
from pathlib import Path
from apps.pack_gateway.supabase_client import save_chat_message

log = logging.getLogger('pack-gateway.chat')

SDC_DIR = Path(os.path.expanduser('~/sonora-digital-corp'))
_OPENROUTER_KEY = None


def _load_openrouter_key():
    global _OPENROUTER_KEY
    if _OPENROUTER_KEY:
        return _OPENROUTER_KEY
    env_path = Path(os.path.expanduser('~/.hermes/.env'))
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith('OPENROUTER_API_KEY='):
                _OPENROUTER_KEY = line.split('=', 1)[1].strip()
                return _OPENROUTER_KEY
    return None


def load_pack(pack_name: str) -> dict | None:
    path = SDC_DIR / 'packs' / pack_name / 'pack.yaml'
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def load_agent(pack_name: str, agent_name: str) -> dict | None:
    path = SDC_DIR / 'packs' / pack_name / 'agents' / f'{agent_name}.yaml'
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_tenant_config(tenant_id: str) -> dict | None:
    path = SDC_DIR / 'config' / 'tenants.json'
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get('tenants', {}).get(tenant_id)


def build_prompt(agent: dict, pack: dict, business_name: str, message: str) -> list[dict]:
    system = agent.get('prompt', '')
    pack_prompts = pack.get('prompts', {})
    primary = pack_prompts.get('primary', '')
    sales = pack_prompts.get('sales', '')

    system = system.replace('{business_name}', business_name)
    primary = primary.replace('{business_name}', business_name)
    sales = sales.replace('{business_name}', business_name)

    skills_desc = []
    for skill_ref in pack.get('skills', []):
        skill_name = skill_ref.split('/')[-1]
        skill_path = SDC_DIR / 'packs' / pack.get('name', '').lower() / 'skills' / f'{skill_name}.yaml'
        if skill_path.exists():
            with open(skill_path) as f:
                sk = yaml.safe_load(f)
            skills_desc.append(f'- {sk.get("name", skill_name)}: {sk.get("description", "")}')

    skills_text = '\n'.join(skills_desc) if skills_desc else 'Ninguna habilidad especifica'
    full_system = f'''{system}

{primary}

{sales}

TUS HABILIDADES:
{skills_text}

IMPORTANTE: Responde en espanol, se profesional y calido.
Siempre pregunta por la ocasion y el presupuesto del cliente.'''

    return [
        {'role': 'system', 'content': full_system},
        {'role': 'user', 'content': message}
    ]


async def chat_with_openrouter(messages: list[dict], tenant_id: str = None, session_id: str = None, user_id: str = None) -> dict:
    import httpx
    key = _load_openrouter_key()
    if not key:
        return {'error': 'OPENROUTER_API_KEY no configurada'}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://sonoradigitalcorp.com',
                'X-Title': 'SDC-Pack-Gateway'
            },
            json={
                'model': 'openrouter/free',
                'messages': messages,
                'max_tokens': 512,
                'temperature': 0.7
            }
        )
        data = resp.json()

    if 'choices' not in data:
        return {'error': data.get('error', {}).get('message', 'Error desconocido')}

    response_text = data['choices'][0]['message']['content'].strip()

    if tenant_id:
        import asyncio
        user_msg = messages[-1]['content'] if messages else ''
        asyncio.ensure_future(save_chat_message(tenant_id, session_id, 'user', user_msg, user_id=user_id))
        asyncio.ensure_future(save_chat_message(tenant_id, session_id, 'assistant', response_text, user_id=user_id))

    return {
        'response': response_text,
        'model': data['model'],
        'tokens': data['usage']['total_tokens']
    }
