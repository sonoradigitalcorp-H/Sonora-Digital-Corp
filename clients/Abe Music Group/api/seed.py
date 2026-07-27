import os
import hashlib
from services.storage import StorageService
from services.auth import AuthService

DATA_DIR = "/home/ubuntu/abe-api/data"

def seed_all():
    if not os.path.exists(os.path.join(DATA_DIR, "services.json")):
        StorageService.save("services", [
            {"id":"1","title":"Digital Distribution","desc":"Multi-platform distribution to Spotify, Apple Music, TikTok, and 150+ streaming services.","icon":"🎵"},
            {"id":"2","title":"Artist Management","desc":"Full-service management including booking, marketing, and career strategy.","icon":"🎤"},
            {"id":"3","title":"Revenue Intelligence","desc":"Real-time royalty tracking, revenue analytics, and predictive modeling.","icon":"📊"},
            {"id":"4","title":"AI Content Factory","desc":"Automated music video production, visualizers, cover art, and social media content.","icon":"🎬"},
            {"id":"5","title":"Fan CRM","desc":"Fan engagement platform with email campaigns, analytics, and segmentation.","icon":"🤝"},
            {"id":"6","title":"Merch Store","desc":"Print-on-demand merch, digital products, and subscription management.","icon":"🛒"},
        ])
        print("Seeded services")

    if not os.path.exists(os.path.join(DATA_DIR, "artists.json")):
        StorageService.save("artists", [
            {"id":"1","name":"Hector Rubio","streams":115000000,"label":"ABE Music Group","image":"🎸","monthly_listeners":1100000,"top_song":"Se Volvieron Locos","top_song_streams":16000000,"instagram":"@hector_rubiorr","spotify_url":"https://open.spotify.com/artist/2uSJ9ywE44eIRoTMatARAy","apple_music_url":"https://music.apple.com/us/artist/hector-rubio/1082292215"},
            {"id":"2","name":"Jesus Urquijo","streams":4600000,"label":"ABE Music Group","image":"🎹","monthly_listeners":29800,"top_song":"Power Trae","top_song_streams":2125681,"instagram":"@jesusurquijo_oficial","spotify_url":"https://open.spotify.com/artist/1hfrbMUDkM2tlUE85D3dR6","apple_music_url":"https://music.apple.com/us/artist/jesus-urquijo/1319826332"},
            {"id":"3","name":"Javier Arvayo","streams":50000,"label":"ABE Music Group","image":"🎤","monthly_listeners":981,"top_song":"GOETT","top_song_streams":25000,"instagram":"","spotify_url":"https://open.spotify.com/artist/0td9IOgiffWGMbcz3xKy0s","apple_music_url":"https://music.apple.com/us/artist/javier-arvayo/1519877798"},
        ])
        print("Seeded artists")

    if not os.path.exists(os.path.join(DATA_DIR, "contacts.json")):
        StorageService.save("contacts", [])
        print("Seeded contacts")

    if not os.path.exists(os.path.join(DATA_DIR, "users.json")):
        salt, hashed = AuthService.hash_password("admin123")
        StorageService.save("users", [
            {"email":"admin@abe.com","password":f"{salt}:{hashed}","role":"admin","name":"Admin"},
            {"email":"demo@abe.com","password":f"{salt}:{hashed}","role":"user","name":"Demo User"},
        ])
        print("Seeded users (admin@abe.com / admin123)")

if __name__ == "__main__":
    seed_all()
