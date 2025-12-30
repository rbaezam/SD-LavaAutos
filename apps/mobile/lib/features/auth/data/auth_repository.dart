import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/services/api_service.dart';
import '../../../shared/services/storage_service.dart';
import 'user_model.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.watch(apiServiceProvider),
    ref.watch(storageServiceProvider),
  );
});

class AuthRepository {
  final ApiService _apiService;
  final StorageService _storageService;

  AuthRepository(this._apiService, this._storageService);

  Future<User> register({
    required String email,
    required String password,
    String? fullName,
  }) async {
    final response = await _apiService.post(
      '/api/v1/auth/register',
      data: {
        'email': email,
        'password': password,
        if (fullName != null) 'full_name': fullName,
      },
    );

    final data = response.data as Map<String, dynamic>;
    await _storageService.saveTokens(
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );

    return getCurrentUser();
  }

  Future<User> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiService.post(
      '/api/v1/auth/login',
      data: {
        'email': email,
        'password': password,
      },
    );

    final data = response.data as Map<String, dynamic>;
    await _storageService.saveTokens(
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );

    return getCurrentUser();
  }

  Future<User> getCurrentUser() async {
    final response = await _apiService.get('/api/v1/auth/me');
    return User.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await _storageService.clearTokens();
  }

  Future<bool> isAuthenticated() async {
    return _storageService.hasTokens();
  }
}
