import { AiOutlineHeadphones } from 'react-icons/ai';
import { useState } from 'react';

function Hero() {
  const [showButton, setShowButton] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-4xl font-bold text-white mb-8">Welcome to ABE Music</h1>
      <p className="text-xl text-white mb-8 text-center w-2/3">
        We are a music production company dedicated to creating the best music experiences for our clients.
      </p>
      <button
        className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-full"
        onClick={() => setShowButton(!showButton)}
        style={{ display: showButton ? 'block' : 'none' }}
      >
        {showButton ? 'Hide' : 'Show'}
        Voice Assistant
      </button>
    </div>
  );
}

export default Hero;
