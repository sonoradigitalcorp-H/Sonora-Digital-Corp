import { AiOutlineHeadphones } from 'react-icons/ai';

function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="flex justify-between">
          <div className="w-1/3">
            <h3 className="text-lg font-medium mb-4">ABE Music</h3>
            <p className="text-sm">We are a music production company dedicated to creating</p>
          </div>
          <div className="w-1/3">
            <h3 className="text-lg font-medium mb-4">Menu</h3>
            <ul className="list-disc pl-4">
              <li><a href="#" className="text-yellow-300 hover:text-yellow-400">Home</a></li>
              <li><a href="#" className="text-yellow-300 hover:text-yellow-400">About</a></li>
              <li><a href="#" className="text-yellow-300 hover:text-yellow-400">Contact</a></li>
            </ul>
          </div>
          <div className="w-1/3">
            <h3 className="text-lg font-medium mb-4">Follow Us</h3>
            <div className="flex space-x-4">
              <a href="#" className="text-yellow-300 hover:text-yellow-400">
                <svg className="fill-current h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5zM2 17l10 5 10-5z" />
                </svg>
                Twitter
              </a>
              <a href="#" className="text-yellow-300 hover:text-yellow-400">
                <svg className="fill-current h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path d="M12 2L2 12l10 2 10-2zM2 7l10 5 10-5M2 12l10 5 10-5" />
                </svg>
                Instagram
              </a>
              <a href="#" className="text-yellow-300 hover:text-yellow-400">
                <svg className="fill-current h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <path d="M12 2L2 12l10 2 10-2zM2 7l10 5 10-5M2 12l10 5 10-5" />
                </svg>
                Facebook
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
