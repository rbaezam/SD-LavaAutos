import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/data/auth_repository.dart';
import '../../features/auth/data/user_model.dart';

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  bool get isAuthenticated => user != null;

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
    bool clearUser = false,
    bool clearError = false,
  }) {
    return AuthState(
      user: clearUser ? null : (user ?? this.user),
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthNotifier extends AsyncNotifier<AuthState> {
  @override
  Future<AuthState> build() async {
    final authRepo = ref.watch(authRepositoryProvider);
    final isAuthenticated = await authRepo.isAuthenticated();

    if (isAuthenticated) {
      try {
        final user = await authRepo.getCurrentUser();
        return AuthState(user: user);
      } catch (_) {
        await authRepo.logout();
        return const AuthState();
      }
    }

    return const AuthState();
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();

    try {
      final authRepo = ref.read(authRepositoryProvider);
      final user = await authRepo.login(email: email, password: password);
      state = AsyncValue.data(AuthState(user: user));
    } catch (e) {
      state = AsyncValue.data(
        AuthState(error: _parseError(e)),
      );
    }
  }

  Future<void> register({
    required String email,
    required String password,
    String? fullName,
  }) async {
    state = const AsyncValue.loading();

    try {
      final authRepo = ref.read(authRepositoryProvider);
      final user = await authRepo.register(
        email: email,
        password: password,
        fullName: fullName,
      );
      state = AsyncValue.data(AuthState(user: user));
    } catch (e) {
      state = AsyncValue.data(
        AuthState(error: _parseError(e)),
      );
    }
  }

  Future<void> logout() async {
    final authRepo = ref.read(authRepositoryProvider);
    await authRepo.logout();
    state = const AsyncValue.data(AuthState());
  }

  void clearError() {
    final currentState = state.valueOrNull;
    if (currentState != null) {
      state = AsyncValue.data(currentState.copyWith(clearError: true));
    }
  }

  String _parseError(dynamic e) {
    if (e.toString().contains('400') || e.toString().contains('401')) {
      return 'Invalid credentials';
    }
    if (e.toString().contains('email already registered')) {
      return 'Email already registered';
    }
    return 'An error occurred. Please try again.';
  }
}

final authStateProvider =
    AsyncNotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);
