// API utility for making requests to Flask backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Get auth token from localStorage
  getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  // Set auth token
  setToken(token) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  // Remove auth token
  removeToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // Get user data
  getUser() {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  // Set user data
  setUser(user) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
  }

  // Remove user data
  removeUser() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
    }
  }

  // Make HTTP request
  async request(endpoint, options = {}) {
    const token = this.getToken();
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  // Auth endpoints
  async register(userData) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
      this.setUser(data.user);
    }
    
    return data;
  }

  async login(phone) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
      this.setUser(data.user);
    }
    
    return data;
  }

  async verifyOTP(idToken, additionalData = {}) {
    const data = await this.request('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ id_token: idToken, ...additionalData }),
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
      this.setUser(data.user);
    }
    
    return data;
  }

  async getProfile() {
    return this.request('/auth/profile');
  }

  async updateProfile(profileData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async changeLanguage(language) {
    return this.request('/auth/change-language', {
      method: 'POST',
      body: JSON.stringify({ language }),
    });
  }

  logout() {
    this.removeToken();
    this.removeUser();
  }

  // Booking endpoints
  async createBooking(bookingData) {
    return this.request('/booking/create', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  }

  async getMyBookings(status = null) {
    const query = status ? `?status=${status}` : '';
    return this.request(`/booking/my-bookings${query}`);
  }

  async getBooking(bookingId) {
    return this.request(`/booking/${bookingId}`);
  }

  async cancelBooking(bookingId) {
    return this.request(`/booking/${bookingId}/cancel`, {
      method: 'POST',
    });
  }

  async rateBooking(bookingId, rating, feedback) {
    return this.request(`/booking/${bookingId}/rate`, {
      method: 'POST',
      body: JSON.stringify({ rating, feedback }),
    });
  }

  async uploadGoodsImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    const token = this.getToken();
    const response = await fetch(`${this.baseUrl}/booking/upload-image`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    return response.json();
  }

  // Driver endpoints
  async registerDriver(driverData) {
    return this.request('/driver/register', {
      method: 'POST',
      body: JSON.stringify(driverData),
    });
  }

  async getDriverProfile() {
    return this.request('/driver/profile');
  }

  async updateDriverStatus(status) {
    return this.request('/driver/status', {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  }

  async updateDriverLocation(latitude, longitude) {
    return this.request('/driver/location', {
      method: 'POST',
      body: JSON.stringify({ latitude, longitude }),
    });
  }

  async getAvailableBookings() {
    return this.request('/booking/driver/available');
  }

  async acceptBooking(bookingId) {
    return this.request(`/booking/${bookingId}/accept`, {
      method: 'POST',
    });
  }

  async updateBookingStatus(bookingId, status) {
    return this.request(`/booking/${bookingId}/update-status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  }

  async getDriverBookings(status = null) {
    const query = status ? `?status=${status}` : '';
    return this.request(`/driver/bookings${query}`);
  }

  async registerVehicle(vehicleData) {
    return this.request('/driver/vehicle/register', {
      method: 'POST',
      body: JSON.stringify(vehicleData),
    });
  }

  // Admin endpoints
  async getDashboard() {
    return this.request('/admin/dashboard');
  }

  async getPendingDrivers() {
    return this.request('/admin/drivers/pending');
  }

  async verifyDriver(driverId, isVerified) {
    return this.request(`/admin/drivers/${driverId}/verify`, {
      method: 'POST',
      body: JSON.stringify({ is_verified: isVerified }),
    });
  }

  async getAllDrivers(filters = {}) {
    const query = new URLSearchParams(filters).toString();
    return this.request(`/admin/drivers?${query}`);
  }

  async getAllBookings(filters = {}) {
    const query = new URLSearchParams(filters).toString();
    return this.request(`/admin/bookings?${query}`);
  }

  async assignDriver(bookingId, driverId) {
    return this.request(`/admin/bookings/${bookingId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ driver_id: driverId }),
    });
  }

  async finalizeBooking(bookingId, finalFare, paymentStatus) {
    return this.request(`/admin/bookings/${bookingId}/finalize`, {
      method: 'POST',
      body: JSON.stringify({ final_fare: finalFare, payment_status: paymentStatus }),
    });
  }

  async getRevenueReport(dateFrom, dateTo) {
    const query = new URLSearchParams({ date_from: dateFrom, date_to: dateTo }).toString();
    return this.request(`/admin/reports/revenue?${query}`);
  }

  // Payment endpoints
  async createPaymentOrder(bookingId, paymentType = 'full') {
    return this.request('/payment/create-order', {
      method: 'POST',
      body: JSON.stringify({ booking_id: bookingId, payment_type: paymentType }),
    });
  }

  async verifyPayment(paymentData) {
    return this.request('/payment/verify', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  }

  async markCashPayment(bookingId, finalFare) {
    return this.request('/payment/cash-payment', {
      method: 'POST',
      body: JSON.stringify({ booking_id: bookingId, final_fare: finalFare }),
    });
  }
}

export const api = new ApiService();
export default api;
