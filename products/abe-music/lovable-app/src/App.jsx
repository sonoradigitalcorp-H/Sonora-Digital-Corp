import { useState } from 'react';
import Hero from './components/Hero';
import ArtistCard from './components/ArtistCard';
import Footer from './components/Footer';
import './index.css';

function App() {
  const [open, setOpen] = useState(false);

  return (
    <div className="bg-gray-900 min-h-screen">
      <header className="bg-opacity-75 bg-gradient-to-r from-yellow-900 to-orange-900 py-4">
        <nav className="container mx-auto px-4">
          <div className="flex justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <img src="https://tailwindui.com/img/logos/workflow-mark-indigo-600.svg" alt="Workflow" className="w-20 h-20 object-cover bg-yellow-500 rounded-full" />
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:items-center">
                <div className="hidden sm:ml-6 sm:flex sm:items-center">
                  <button
                    className="inline-flex items-center bg-transparent text-yellow-400 border border-yellow-400 rounded-md py-1 px-3 focus:outline-none hover:bg-yellow-500 hover:text-white transition-colors"
                    onClick={() => setOpen(!open)}
                  >
                    <svg
                      className="fill-current h-4 w-4"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M4 6h16v4H4V6zm0 8h16v4H4v-4zM4 18h16v4H4v-4z"
                      />
                    </svg>
                    <span className="ml-3 text-sm font-medium">Menu</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Hero />
        <section className="my-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <ArtistCard artist="Hector" />
            <ArtistCard artist="Jesus" />
            <ArtistCard artist="Javier" />
          </div>
        </section>
      </main>

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
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
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
    </div>
  );
}

export default App;
