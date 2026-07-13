import { AiOutlineHeadphones } from 'react-icons/ai';

function ArtistCard({ artist }) {
  return (
    <div className="bg-gray-800 text-white rounded-lg overflow-hidden shadow-md">
      <div className="flex flex-col md:flex-row">
        <div className="md:w-1/3 bg-gray-800/30 p-4">
          <img src={`/artists/${artist}.jpg`} alt={artist} className="w-full rounded-t-lg" />
        </div>
        <div className="md:w-2/3 p-4">
          <h2 className="text-xl font-bold mb-2">{artist}</h2>
          <p className="text-gray-300 text-sm">
            {`${artist} is a talented musician who has been creating music for over 10 years.
            He has released several albums and has toured extensively throughout the US and Europe.`}
          </p>
          <div className="mt-4">
            <a href="#" className="inline-flex items-center bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-1 px-3 rounded-full">
              Listen Now
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ArtistCard;
