import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useTranslation } from '../utils/translations';
import { api } from '../utils/api';

export default function DriverDashboard() {
  const router = useRouter();
  const [language, setLanguage] = useState('en');
  const { t } = useTranslation(language);
  const [driver, setDriver] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [availableBookings, setAvailableBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('offline');
  const [activeTab, setActiveTab] = useState('available');

  useEffect(() => {
    const storedLang = typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en';
    setLanguage(storedLang);

    const user = api.getUser();
    if (!user || user.role !== 'driver') {
      router.push('/login');
      return;
    }

    loadDriverData();
  }, []);

  const loadDriverData = async () => {
    try {
      const [driverData, bookingsData, availableData] = await Promise.all([
        api.getDriverProfile(),
        api.getDriverBookings(),
        api.getAvailableBookings()
      ]);

      setDriver(driverData.driver);
      setBookings(bookingsData.bookings || []);
      setAvailableBookings(availableData.bookings || []);
      setStatus(driverData.driver?.status || 'offline');
    } catch (error) {
      console.error('Failed to load driver data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusToggle = async () => {
    try {
      const newStatus = status === 'available' ? 'offline' : 'available';
      await api.updateDriverStatus(newStatus);
      setStatus(newStatus);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const handleAcceptBooking = async (bookingId) => {
    try {
      await api.acceptBooking(bookingId);
      loadDriverData();
      alert(language === 'en' ? 'Booking accepted!' : 'బుకింగ్ ఆమోదించబడింది!');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleUpdateStatus = async (bookingId, newStatus) => {
    try {
      await api.updateBookingStatus(bookingId, newStatus);
      loadDriverData();
    } catch (error) {
      alert(error.message);
    }
  };

  const getStatusColor = (bookingStatus) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      driver_assigned: 'bg-blue-100 text-blue-800',
      driver_reached: 'bg-purple-100 text-purple-800',
      ongoing: 'bg-indigo-100 text-indigo-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[bookingStatus] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">{t('loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <div className="flex-grow py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header with Stats */}
          <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-xl shadow-lg p-6 mb-8 text-white">
            <div className="flex flex-wrap justify-between items-center">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold mb-2">
                  {t('driverDashboard')}
                </h1>
                <p className="text-orange-100">
                  {language === 'en' ? 'Manage your trips and earnings' : 'మీ ట్రిప్‌లు మరియు ఆదాయాన్ని నిర్వహించండి'}
                </p>
              </div>
              <div>
                <button
                  onClick={handleStatusToggle}
                  className={`px-6 py-3 rounded-lg font-bold text-white transition ${
                    status === 'available' 
                      ? 'bg-green-500 hover:bg-green-600' 
                      : 'bg-gray-500 hover:bg-gray-600'
                  }`}
                >
                  {status === 'available' ? '🟢 ' : '⚫ '}
                  {status === 'available' 
                    ? (language === 'en' ? 'Available' : 'అందుబాటులో')
                    : (language === 'en' ? 'Go Online' : 'ఆన్‌లైన్ అవ్వండి')}
                </button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white bg-opacity-20 rounded-lg p-4">
                <div className="text-2xl font-bold">{driver?.total_trips || 0}</div>
                <div className="text-sm text-orange-100">{t('totalTrips')}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-4">
                <div className="text-2xl font-bold">₹{driver?.total_earnings?.toFixed(0) || 0}</div>
                <div className="text-sm text-orange-100">{t('totalEarnings')}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-4">
                <div className="text-2xl font-bold">₹{driver?.wallet_balance?.toFixed(0) || 0}</div>
                <div className="text-sm text-orange-100">
                  {language === 'en' ? 'Wallet' : 'వాలెట్'}
                </div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-4">
                <div className="text-2xl font-bold">{driver?.rating?.toFixed(1) || 0}⭐</div>
                <div className="text-sm text-orange-100">{t('rating')}</div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-lg shadow-md mb-6">
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab('available')}
                className={`flex-1 px-6 py-4 font-medium ${
                  activeTab === 'available'
                    ? 'text-orange-600 border-b-2 border-orange-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {language === 'en' ? 'Available Bookings' : 'అందుబాటులో ఉన్న బుకింగ్‌లు'}
                {availableBookings.length > 0 && (
                  <span className="ml-2 bg-orange-600 text-white text-xs px-2 py-1 rounded-full">
                    {availableBookings.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('my-bookings')}
                className={`flex-1 px-6 py-4 font-medium ${
                  activeTab === 'my-bookings'
                    ? 'text-orange-600 border-b-2 border-orange-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {language === 'en' ? 'My Trips' : 'నా ట్రిప్‌లు'}
              </button>
            </div>
          </div>

          {/* Content */}
          {activeTab === 'available' ? (
            <div className="space-y-4">
              {availableBookings.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <div className="text-gray-400 text-6xl mb-4">📭</div>
                  <p className="text-gray-600">
                    {language === 'en' 
                      ? 'No bookings available right now. Check back later!' 
                      : 'ప్రస్తుతం బుకింగ్‌లు అందుబాటులో లేవు. తర్వాత తనిఖీ చేయండి!'}
                  </p>
                </div>
              ) : (
                availableBookings.map((booking) => (
                  <div key={booking.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">
                          {booking.booking_id}
                        </h3>
                        <p className="text-sm text-gray-600">{booking.customer_name}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(booking.status)}`}>
                        {booking.status}
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">📍 {t('pickupAddress')}</p>
                        <p className="font-medium">{booking.pickup.address}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">📍 {t('dropAddress')}</p>
                        <p className="font-medium">{booking.drop.address}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">{t('goodsType')}</p>
                        <p className="font-medium">{booking.goods.type}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{t('distance')}</p>
                        <p className="font-medium">{booking.distance_km} km</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{t('estimatedFare')}</p>
                        <p className="font-medium text-orange-600">₹{booking.estimated_fare}</p>
                      </div>
                    </div>

                    {booking.distance_from_driver && (
                      <p className="text-sm text-gray-600 mb-4">
                        🚗 {booking.distance_from_driver.toFixed(1)} km {language === 'en' ? 'away from you' : 'మీకు దూరంలో'}
                      </p>
                    )}

                    <button
                      onClick={() => handleAcceptBooking(booking.id)}
                      className="w-full bg-gradient-to-r from-orange-600 to-red-600 text-white py-3 rounded-lg font-bold hover:from-orange-700 hover:to-red-700 transition"
                    >
                      {t('acceptBooking')} →
                    </button>
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {bookings.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <div className="text-gray-400 text-6xl mb-4">🚚</div>
                  <p className="text-gray-600">
                    {language === 'en' 
                      ? 'No trips yet. Accept bookings to get started!' 
                      : 'ఇంకా ట్రిప్‌లు లేవు. ప్రారంభించడానికి బుకింగ్‌లను ఆమోదించండి!'}
                  </p>
                </div>
              ) : (
                bookings.map((booking) => (
                  <div key={booking.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{booking.booking_id}</h3>
                        <p className="text-sm text-gray-600">{booking.customer_name}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(booking.status)}`}>
                        {booking.status}
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">📍 {t('pickupAddress')}</p>
                        <p className="font-medium">{booking.pickup.address}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">📍 {t('dropAddress')}</p>
                        <p className="font-medium">{booking.drop.address}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">{t('goodsType')}</p>
                        <p className="font-medium">{booking.goods.type}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{t('distance')}</p>
                        <p className="font-medium">{booking.distance_km} km</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">
                          {language === 'en' ? 'Earning' : 'ఆదాయం'}
                        </p>
                        <p className="font-medium text-orange-600">
                          ₹{booking.driver_earning || booking.estimated_fare}
                        </p>
                      </div>
                    </div>

                    {booking.status === 'driver_assigned' && (
                      <button
                        onClick={() => handleUpdateStatus(booking.id, 'driver_reached')}
                        className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
                      >
                        {language === 'en' ? 'Mark as Reached' : 'చేరుకున్నట్లు గుర్తించండి'}
                      </button>
                    )}

                    {booking.status === 'driver_reached' && (
                      <button
                        onClick={() => handleUpdateStatus(booking.id, 'ongoing')}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 transition"
                      >
                        {t('startTrip')}
                      </button>
                    )}

                    {booking.status === 'ongoing' && (
                      <button
                        onClick={() => handleUpdateStatus(booking.id, 'completed')}
                        className="w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 transition"
                      >
                        {t('completeTrip')}
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
}
