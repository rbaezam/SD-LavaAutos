class AppConfig {
  // API Configuration
  // For Android emulator, use 10.0.2.2 instead of localhost
  // For iOS simulator, use localhost
  // For physical devices, use your machine's IP address
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  // Connection timeout in seconds
  static const int connectTimeout = 30;
  static const int receiveTimeout = 30;
}
