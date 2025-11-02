import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useTranslation } from '../utils/translations';
import { api } from '../utils/api';

export default function Home() {
  const [language, setLanguage] = useState('en');
  const [user, setUser] = useState(null);
  const { t } = useTranslation(language);

  useEffect(() => {
    const storedLang = typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en';
    setLanguage(storedLang);
    setUser(api.getUser());
  }, []);

  const features = [
    {
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      titleEn: 'Fast Booking',
      titleTe: 'వేగవంతమైన బుకింగ్',
      descEn: 'Book a DCM in minutes with our easy-to-use platform',
      descTe: 'మా సులభమైన ప్లాట్‌ఫారమ్‌తో నిమిషాల్లో DCM బుక్ చేయండి'
    },
    {
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      titleEn: 'Verified Drivers',
      titleTe: 'ధృవీకరించబడిన డ్రైవర్లు',
      descEn: '100+ verified and trusted DCM drivers across Telangana',
      descTe: 'తెలంగాణ అంతటా 100+ ధృవీకరించబడిన మరియు విశ్వసనీయ DCM డ్రైవర్లు'
    },
    {
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      titleEn: 'Best Rates',
      titleTe: 'మంచి ధరలు',
      descEn: 'Competitive pricing with transparent fare calculation',
      descTe: 'పారదర్శక ధర లెక్కింపుతో పోటీ ధరలు'
    },
    {
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
      ),
      titleEn: '24/7 Support',
      titleTe: '24/7 మద్దతు',
      descEn: 'Round-the-clock customer support for your convenience',
      descTe: 'మీ సౌకర్యం కోసం రౌండ్-ది-క్లాక్ కస్టమర్ సపోర్ట్'
    }
  ];

  const goodsTypes = [
    { nameEn: 'Cement & Bricks', nameTe: 'సిమెంట్ & ఇటుకలు', icon: '🏗️' },
    { nameEn: 'Furniture', nameTe: 'ఫర్నిచర్', icon: '🪑' },
    { nameEn: 'Electronics', nameTe: 'ఎలక్ట్రానిక్స్', icon: '📺' },
    { nameEn: 'Agricultural', nameTe: 'వ్యవసాయం', icon: '🌾' },
    { nameEn: 'Household Items', nameTe: 'గృహ సామగ్రి', icon: '🏠' },
    { nameEn: 'Machinery', nameTe: 'యంత్రాలు', icon: '⚙️' }
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                {language === 'en' 
                  ? 'Your Trusted Transport Partner in Telangana'
                  : 'తెలంగాణలో మీ విశ్వసనీయ రవాణా భాగస్వామి'}
              </h1>
              <p className="text-xl mb-8 text-orange-100">
                {language === 'en'
                  ? 'Book DCM vehicles for cement, furniture, and all your goods transportation needs across Telangana'
                  : 'తెలంగాణ అంతటా సిమెంట్, ఫర్నిచర్ మరియు మీ అన్ని సరుకుల రవాణా అవసరాలకు DCM వాహనాలను బుక్ చేయండి'}
              </p>
              <div className="flex flex-wrap gap-4">
                {user ? (
                  <Link href="/book">
                    <a className="bg-white text-orange-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-orange-50 transition shadow-lg">
                      {t('bookNow')} →
                    </a>
                  </Link>
                ) : (
                  <>
                    <Link href="/register">
                      <a className="bg-white text-orange-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-orange-50 transition shadow-lg">
                        {language === 'en' ? 'Get Started' : 'ప్రారంభించండి'} →
                      </a>
                    </Link>
                    <Link href="/login">
                      <a className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white hover:text-orange-600 transition">
                        {t('login')}
                      </a>
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="hidden md:block">
              <div className="bg-white bg-opacity-10 backdrop-blur-sm p-8 rounded-2xl">
                <div className="text-center">
                  <div className="text-6xl mb-4">🚚</div>
                  <h3 className="text-2xl font-bold mb-4">
                    {language === 'en' ? 'Quick Stats' : 'త్వరిత గణాంకాలు'}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white bg-opacity-20 p-4 rounded-lg">
                      <div className="text-3xl font-bold">100+</div>
                      <div className="text-sm">{language === 'en' ? 'Drivers' : 'డ్రైవర్లు'}</div>
                    </div>
                    <div className="bg-white bg-opacity-20 p-4 rounded-lg">
                      <div className="text-3xl font-bold">500+</div>
                      <div className="text-sm">{language === 'en' ? 'Trips' : 'ట్రిప్‌లు'}</div>
                    </div>
                    <div className="bg-white bg-opacity-20 p-4 rounded-lg">
                      <div className="text-3xl font-bold">50+</div>
                      <div className="text-sm">{language === 'en' ? 'Cities' : 'నగరాలు'}</div>
                    </div>
                    <div className="bg-white bg-opacity-20 p-4 rounded-lg">
                      <div className="text-3xl font-bold">4.8⭐</div>
                      <div className="text-sm">{language === 'en' ? 'Rating' : 'రేటింగ్'}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === 'en' ? 'Why Choose Us?' : 'మమ్మల్ని ఎందుకు ఎంచుకోవాలి?'}
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition text-center">
                <div className="text-orange-600 mb-4 flex justify-center">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-2">
                  {language === 'en' ? feature.titleEn : feature.titleTe}
                </h3>
                <p className="text-gray-600">
                  {language === 'en' ? feature.descEn : feature.descTe}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Goods Types */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === 'en' ? 'What We Transport' : 'మేము ఏమి రవాణా చేస్తాము'}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {goodsTypes.map((type, index) => (
              <div key={index} className="text-center p-6 bg-orange-50 rounded-lg hover:bg-orange-100 transition">
                <div className="text-4xl mb-3">{type.icon}</div>
                <div className="font-semibold text-gray-800">
                  {language === 'en' ? type.nameEn : type.nameTe}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === 'en' ? 'How It Works' : 'ఇది ఎలా పనిచేస్తుంది'}
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-orange-600 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
              <h3 className="text-xl font-bold mb-2">
                {language === 'en' ? 'Enter Details' : 'వివరాలు నమోదు చేయండి'}
              </h3>
              <p className="text-gray-600">
                {language === 'en' 
                  ? 'Enter pickup, drop location, and goods details'
                  : 'పికప్, డ్రాప్ లొకేషన్ మరియు సరుకుల వివరాలు నమోదు చేయండి'}
              </p>
            </div>
            <div className="text-center">
              <div className="bg-orange-600 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
              <h3 className="text-xl font-bold mb-2">
                {language === 'en' ? 'Get Driver' : 'డ్రైవర్ పొందండి'}
              </h3>
              <p className="text-gray-600">
                {language === 'en'
                  ? 'We assign nearest verified driver instantly'
                  : 'మేము తక్షణమే సమీపంలోని ధృవీకరించబడిన డ్రైవర్‌ను కేటాయిస్తాము'}
              </p>
            </div>
            <div className="text-center">
              <div className="bg-orange-600 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
              <h3 className="text-xl font-bold mb-2">
                {language === 'en' ? 'Track & Deliver' : 'ట్రాక్ & డెలివరీ'}
              </h3>
              <p className="text-gray-600">
                {language === 'en'
                  ? 'Track your goods and get them delivered safely'
                  : 'మీ సరుకులను ట్రాక్ చేయండి మరియు సురక్షితంగా డెలివరీ పొందండి'}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            {language === 'en' 
              ? 'Ready to Transport Your Goods?'
              : 'మీ సరుకులను రవాణా చేయడానికి సిద్ధంగా ఉన్నారా?'}
          </h2>
          <p className="text-xl mb-8 text-orange-100">
            {language === 'en'
              ? 'Join thousands of satisfied customers across Telangana'
              : 'తెలంగాణ అంతటా వేలాది సంతృప్తి చెందిన కస్టమర్‌లతో చేరండి'}
          </p>
          {user ? (
            <Link href="/book">
              <a className="bg-white text-orange-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-orange-50 transition inline-block shadow-lg">
                {t('bookNow')} →
              </a>
            </Link>
          ) : (
            <Link href="/register">
              <a className="bg-white text-orange-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-orange-50 transition inline-block shadow-lg">
                {language === 'en' ? 'Sign Up Now' : 'ఇప్పుడే సైన్ అప్ చేయండి'} →
              </a>
            </Link>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
}
