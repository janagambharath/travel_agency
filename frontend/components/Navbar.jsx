import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { api } from '../utils/api';
import { useTranslation } from '../utils/translations';

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [language, setLanguage] = useState('en');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { t } = useTranslation(language);

  useEffect(() => {
    // Load user and language from localStorage
    const storedUser = api.getUser();
    const storedLang = typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en';
    
    setUser(storedUser);
    setLanguage(storedLang);
  }, []);

  const handleLanguageToggle = async () => {
    const newLang = language === 'en' ? 'te' : 'en';
    setLanguage(newLang);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('language', newLang);
    }

    // Update on server if logged in
    if (user) {
      try {
        await api.changeLanguage(newLang);
      } catch (error) {
        console.error('Failed to update language:', error);
      }
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    router.push('/');
  };

  return (
    <nav className="bg-gradient-to-r from-orange-600 to-red-600 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link href="/">
              <div className="flex items-center cursor-pointer">
                <div className="bg-white p-2 rounded-lg">
                  <svg className="h-8 w-8 text-orange-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18 18.5a1.5 1.5 0 01-1.5-1.5V9c0-2.206-1.794-4-4-4S8.5 6.794 8.5 9v8a1.5 1.5 0 01-3 0V9c0-3.859 3.141-7 7-7s7 3.141 7 7v8a1.5 1.5 0 01-1.5 1.5z"/>
                    <path d="M12 22a3 3 0 100-6 3 3 0 000 6z"/>
                  </svg>
                </div>
                <div className="ml-3">
                  <h1 className="text-white font-bold text-lg">
                    {language === 'en' ? 'Sri Ramalingeshvara' : 'శ్రీ రామలింగేశ్వర'}
                  </h1>
                  <p className="text-orange-100 text-xs">
                    {language === 'en' ? 'Transport Services' : 'ట్రాన్స్‌పోర్ట్ సేవలు'}
                  </p>
                </div>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link href="/">
              <a className="text-white hover:text-orange-100 transition">{t('home')}</a>
            </Link>
            
            {user ? (
              <>
                {user.role === 'customer' && (
                  <>
                    <Link href="/book">
                      <a className="text-white hover:text-orange-100 transition">{t('bookNow')}</a>
                    </Link>
                    <Link href="/my-bookings">
                      <a className="text-white hover:text-orange-100 transition">{t('myBookings')}</a>
                    </Link>
                  </>
                )}
                
                {user.role === 'driver' && (
                  <Link href="/driver">
                    <a className="text-white hover:text-orange-100 transition">{t('driverDashboard')}</a>
                  </Link>
                )}
                
                {user.role === 'admin' && (
                  <Link href="/admin">
                    <a className="text-white hover:text-orange-100 transition">{t('adminPanel')}</a>
                  </Link>
                )}
                
                <Link href="/profile">
                  <a className="text-white hover:text-orange-100 transition">{t('profile')}</a>
                </Link>
                
                <button
                  onClick={handleLogout}
                  className="bg-white text-orange-600 px-4 py-2 rounded-lg hover:bg-orange-50 transition font-medium"
                >
                  {t('logout')}
                </button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <a className="text-white hover:text-orange-100 transition">{t('login')}</a>
                </Link>
                <Link href="/register">
                  <a className="bg-white text-orange-600 px-4 py-2 rounded-lg hover:bg-orange-50 transition font-medium">
                    {t('register')}
                  </a>
                </Link>
              </>
            )}

            {/* Language Toggle */}
            <button
              onClick={handleLanguageToggle}
              className="flex items-center bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg transition"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
              <span className="font-medium">{language === 'en' ? 'తె' : 'EN'}</span>
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={handleLanguageToggle}
              className="bg-white bg-opacity-20 text-white p-2 rounded-lg"
            >
              <span className="font-medium text-sm">{language === 'en' ? 'తె' : 'EN'}</span>
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-white p-2"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4">
            <div className="flex flex-col space-y-3">
              <Link href="/">
                <a className="text-white hover:text-orange-100 py-2">{t('home')}</a>
              </Link>
              
              {user ? (
                <>
                  {user.role === 'customer' && (
                    <>
                      <Link href="/book">
                        <a className="text-white hover:text-orange-100 py-2">{t('bookNow')}</a>
                      </Link>
                      <Link href="/my-bookings">
                        <a className="text-white hover:text-orange-100 py-2">{t('myBookings')}</a>
                      </Link>
                    </>
                  )}
                  
                  {user.role === 'driver' && (
                    <Link href="/driver">
                      <a className="text-white hover:text-orange-100 py-2">{t('driverDashboard')}</a>
                    </Link>
                  )}
                  
                  {user.role === 'admin' && (
                    <Link href="/admin">
                      <a className="text-white hover:text-orange-100 py-2">{t('adminPanel')}</a>
                    </Link>
                  )}
                  
                  <Link href="/profile">
                    <a className="text-white hover:text-orange-100 py-2">{t('profile')}</a>
                  </Link>
                  
                  <button
                    onClick={handleLogout}
                    className="bg-white text-orange-600 px-4 py-2 rounded-lg hover:bg-orange-50 transition text-left font-medium"
                  >
                    {t('logout')}
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login">
                    <a className="text-white hover:text-orange-100 py-2">{t('login')}</a>
                  </Link>
                  <Link href="/register">
                    <a className="bg-white text-orange-600 px-4 py-2 rounded-lg hover:bg-orange-50 transition font-medium">
                      {t('register')}
                    </a>
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
