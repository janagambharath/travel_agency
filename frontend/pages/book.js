import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useTranslation } from '../utils/translations';
import { api } from '../utils/api';

export default function BookPage() {
  const router = useRouter();
  const [language, setLanguage] = useState('en');
  const { t } = useTranslation(language);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    pickup_address: '',
    pickup_latitude: null,
    pickup_longitude: null,
    pickup_city: '',
    drop_address: '',
    drop_latitude: null,
    drop_longitude: null,
    drop_city: '',
    goods_type: '',
    weight_kg: '',
    volume_cubic_ft: '',
    special_instructions: '',
    scheduled_date: ''
  });

  const [estimatedFare, setEstimatedFare] = useState(null);
  const [distance, setDistance] = useState(null);

  useEffect(() => {
    const storedLang = typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en';
    setLanguage(storedLang);

    // Check if user is logged in
    const user = api.getUser();
    if (!user || user.role !== 'customer') {
      router.push('/login');
    }
  }, []);

  const goodsTypes = [
    { value: 'cement', labelEn: 'Cement', labelTe: 'సిమెంట్' },
    { value: 'bricks', labelEn: 'Bricks', labelTe: 'ఇటుకలు' },
    { value: 'sand', labelEn: 'Sand', labelTe: 'ఇసుక' },
    { value: 'gravel', labelEn: 'Gravel', labelTe: 'గులకరాళ్ళు' },
    { value: 'furniture', labelEn: 'Furniture', labelTe: 'ఫర్నిచర్' },
    { value: 'electronics', labelEn: 'Electronics', labelTe: 'ఎలక్ట్రానిక్స్' },
    { value: 'household', labelEn: 'Household Items', labelTe: 'గృహ సామగ్రి' },
    { value: 'machinery', labelEn: 'Machinery', labelTe: 'యంత్రాలు' },
    { value: 'agricultural', labelEn: 'Agricultural Goods', labelTe: 'వ్యవసాయ సామాగ్రి' },
    { value: 'food_items', labelEn: 'Food Items', labelTe: 'ఆహార పదార్థాలు' },
    { value: 'textiles', labelEn: 'Textiles', labelTe: 'వస్త్రాలు' },
    { value: 'others', labelEn: 'Others', labelTe: 'ఇతరాలు' }
  ];

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const calculateEstimate = () => {
    // Mock calculation - in real app, use Google Maps API
    if (formData.pickup_latitude && formData.drop_latitude) {
      const mockDistance = 25; // km
      const baseFare = 150;
      const perKm = 15;
      const fare = baseFare + (mockDistance * perKm);
      
      setDistance(mockDistance);
      setEstimatedFare(fare);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Mock coordinates for demo
      const bookingData = {
        ...formData,
        pickup_latitude: 17.4065, // Hyderabad
        pickup_longitude: 78.4772,
        drop_latitude: 17.3850,
        drop_longitude: 78.4867
      };

      const response = await api.createBooking(bookingData);
      
      setSuccess(t('bookingSuccess'));
      
      setTimeout(() => {
        router.push('/my-bookings');
      }, 2000);
    } catch (err) {
      setError(err.message || t('bookingFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <div className="flex-grow py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              {t('bookDCM')}
            </h1>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {success && (
              <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
                <p className="text-green-700">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Pickup Address */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('pickupAddress')} *
                </label>
                <input
                  type="text"
                  name="pickup_address"
                  value={formData.pickup_address}
                  onChange={handleInputChange}
                  required
                  placeholder={language === 'en' ? 'Enter pickup location' : 'పికప్ లొకేషన్ నమోదు చేయండి'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* Drop Address */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('dropAddress')} *
                </label>
                <input
                  type="text"
                  name="drop_address"
                  value={formData.drop_address}
                  onChange={handleInputChange}
                  required
                  placeholder={language === 'en' ? 'Enter drop location' : 'డ్రాప్ లొకేషన్ నమోదు చేయండి'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* Goods Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('goodsType')} *
                </label>
                <select
                  name="goods_type"
                  value={formData.goods_type}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="">{t('selectGoods')}</option>
                  {goodsTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {language === 'en' ? type.labelEn : type.labelTe}
                    </option>
                  ))}
                </select>
              </div>

              {/* Weight and Volume */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('weight')}
                  </label>
                  <input
                    type="number"
                    name="weight_kg"
                    value={formData.weight_kg}
                    onChange={handleInputChange}
                    placeholder="kg"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('volume')}
                  </label>
                  <input
                    type="number"
                    name="volume_cubic_ft"
                    value={formData.volume_cubic_ft}
                    onChange={handleInputChange}
                    placeholder="cubic ft"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Schedule Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('scheduleDate')} *
                </label>
                <input
                  type="datetime-local"
                  name="scheduled_date"
                  value={formData.scheduled_date}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              {/* Special Instructions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('specialInstructions')}
                </label>
                <textarea
                  name="special_instructions"
                  value={formData.special_instructions}
                  onChange={handleInputChange}
                  rows="3"
                  placeholder={language === 'en' ? 'Any special requirements...' : 'ఏదైనా ప్రత్యేక అవసరాలు...'}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                ></textarea>
              </div>

              {/* Estimate Display */}
              {estimatedFare && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">{t('distance')}:</span>
                    <span className="text-gray-900 font-bold">{distance} km</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700 font-medium">{t('estimatedFare')}:</span>
                    <span className="text-orange-600 text-2xl font-bold">₹{estimatedFare}</span>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={calculateEstimate}
                  className="flex-1 bg-gray-100 text-gray-700 py-4 rounded-lg font-bold hover:bg-gray-200 transition"
                >
                  {language === 'en' ? 'Calculate Fare' : 'ధర లెక్కించండి'}
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-red-600 text-white py-4 rounded-lg font-bold hover:from-orange-700 hover:to-red-700 transition disabled:opacity-50"
                >
                  {loading ? t('loading') : t('createBooking')}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
