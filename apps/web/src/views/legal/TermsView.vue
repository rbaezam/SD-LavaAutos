<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Droplets, ArrowLeft } from 'lucide-vue-next'

const lastUpdated = '29 de diciembre de 2024'
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between">
          <RouterLink to="/" class="flex items-center gap-2">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
              <Droplets class="h-5 w-5" />
            </div>
            <span class="text-xl font-bold">WashFlow</span>
          </RouterLink>
          <RouterLink
            to="/"
            class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft class="h-4 w-4" />
            Volver al inicio
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="space-y-8">
        <div class="space-y-4">
          <h1 class="text-4xl font-bold tracking-tight">Términos de Servicio</h1>
          <p class="text-muted-foreground">Última actualización: {{ lastUpdated }}</p>
        </div>

        <div class="prose prose-gray max-w-none">
          <section class="space-y-4">
            <h2 class="text-2xl font-semibold">1. Aceptación de los Términos</h2>
            <p class="text-muted-foreground leading-relaxed">
              Al acceder y utilizar WashFlow ("el Servicio"), usted acepta estar sujeto a estos
              Términos de Servicio. Si no está de acuerdo con alguna parte de estos términos,
              no podrá acceder al Servicio.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">2. Descripción del Servicio</h2>
            <p class="text-muted-foreground leading-relaxed">
              WashFlow es una plataforma de gestión para negocios de autolavado que permite:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Gestionar tickets y servicios de lavado</li>
              <li>Notificar a los clientes sobre el estado de sus vehículos</li>
              <li>Visualizar métricas y reportes del negocio</li>
              <li>Administrar múltiples sucursales</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">3. Cuentas de Usuario</h2>
            <p class="text-muted-foreground leading-relaxed">
              Para utilizar ciertas funciones del Servicio, debe crear una cuenta. Usted es
              responsable de:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Mantener la confidencialidad de su contraseña</li>
              <li>Todas las actividades que ocurran bajo su cuenta</li>
              <li>Notificarnos inmediatamente sobre cualquier uso no autorizado</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">4. Planes y Pagos</h2>
            <p class="text-muted-foreground leading-relaxed">
              WashFlow ofrece diferentes planes de suscripción. Los precios están expresados
              en Pesos Mexicanos (MXN) e incluyen IVA. Los pagos se procesan de forma mensual
              y se renuevan automáticamente hasta que se cancele la suscripción.
            </p>
            <p class="text-muted-foreground leading-relaxed mt-2">
              El plan gratuito está disponible con funcionalidades limitadas y sin compromiso
              de pago.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">5. Uso Aceptable</h2>
            <p class="text-muted-foreground leading-relaxed">
              Al utilizar el Servicio, usted se compromete a no:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Violar leyes o regulaciones aplicables</li>
              <li>Interferir con el funcionamiento del Servicio</li>
              <li>Intentar acceder a cuentas de otros usuarios</li>
              <li>Transmitir contenido malicioso o dañino</li>
              <li>Utilizar el Servicio para fines ilegales</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">6. Propiedad Intelectual</h2>
            <p class="text-muted-foreground leading-relaxed">
              El Servicio y su contenido original, características y funcionalidad son propiedad
              de WashFlow y están protegidos por leyes de propiedad intelectual. Usted conserva
              todos los derechos sobre los datos que ingrese al sistema.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">7. Privacidad</h2>
            <p class="text-muted-foreground leading-relaxed">
              El uso del Servicio está sujeto a nuestra
              <RouterLink to="/privacy" class="text-primary hover:underline">
                Política de Privacidad
              </RouterLink>, que describe cómo recopilamos, usamos y protegemos su información.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">8. Limitación de Responsabilidad</h2>
            <p class="text-muted-foreground leading-relaxed">
              En la máxima medida permitida por la ley, WashFlow no será responsable de daños
              indirectos, incidentales, especiales, consecuentes o punitivos, ni de cualquier
              pérdida de beneficios o ingresos.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">9. Modificaciones</h2>
            <p class="text-muted-foreground leading-relaxed">
              Nos reservamos el derecho de modificar estos términos en cualquier momento.
              Le notificaremos sobre cambios significativos a través del correo electrónico
              asociado a su cuenta o mediante un aviso en el Servicio.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">10. Contacto</h2>
            <p class="text-muted-foreground leading-relaxed">
              Si tiene preguntas sobre estos Términos de Servicio, puede contactarnos en:
            </p>
            <p class="text-muted-foreground mt-2">
              <a href="mailto:legal@washflow.mx" class="text-primary hover:underline">
                legal@washflow.mx
              </a>
            </p>
          </section>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t bg-muted/30 py-8">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-muted-foreground">
            © 2024 WashFlow. Todos los derechos reservados.
          </p>
          <div class="flex items-center gap-6">
            <RouterLink
              to="/privacy"
              class="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Política de Privacidad
            </RouterLink>
            <a
              href="mailto:hola@washflow.mx"
              class="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Contacto
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
