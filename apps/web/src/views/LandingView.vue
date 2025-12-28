<script setup lang="ts">
import {
  LandingNav,
  LandingHero,
  LandingProblem,
  LandingHowItWorks,
  LandingBenefits,
  LandingProduct,
  LandingAudience,
  LandingPricing,
  LandingCTA,
  LandingFooter,
} from '@/components/landing'
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <LandingNav />

    <!-- Main content -->
    <main>
      <!-- Hero Section -->
      <LandingHero />

      <!-- Problem Section -->
      <LandingProblem />

      <!-- How it Works Section -->
      <LandingHowItWorks />

      <!-- Benefits Section -->
      <LandingBenefits />

      <!-- Product Section -->
      <LandingProduct />

      <!-- Audience Section -->
      <LandingAudience />

      <!-- Pricing Section -->
      <LandingPricing />

      <!-- Final CTA Section -->
      <LandingCTA />
    </main>

    <!-- Footer -->
    <LandingFooter />
  </div>
</template>
