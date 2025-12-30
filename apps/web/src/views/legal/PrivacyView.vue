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
          <h1 class="text-4xl font-bold tracking-tight">Política de Privacidad</h1>
          <p class="text-muted-foreground">Última actualización: {{ lastUpdated }}</p>
        </div>

        <div class="prose prose-gray max-w-none">
          <section class="space-y-4">
            <h2 class="text-2xl font-semibold">1. Información que Recopilamos</h2>
            <p class="text-muted-foreground leading-relaxed">
              En WashFlow recopilamos información que usted nos proporciona directamente:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li><strong>Información de cuenta:</strong> nombre, correo electrónico, contraseña</li>
              <li><strong>Información del negocio:</strong> nombre del autolavado, sucursales, servicios</li>
              <li><strong>Datos operativos:</strong> tickets, clientes, vehículos, transacciones</li>
              <li><strong>Información de uso:</strong> cómo interactúa con nuestro Servicio</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">2. Cómo Utilizamos su Información</h2>
            <p class="text-muted-foreground leading-relaxed">
              Utilizamos la información recopilada para:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Proporcionar, mantener y mejorar el Servicio</li>
              <li>Procesar transacciones y enviar notificaciones relacionadas</li>
              <li>Enviar comunicaciones sobre actualizaciones y nuevas funciones</li>
              <li>Responder a sus solicitudes de soporte</li>
              <li>Detectar y prevenir fraudes o abusos</li>
              <li>Cumplir con obligaciones legales</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">3. Compartición de Información</h2>
            <p class="text-muted-foreground leading-relaxed">
              No vendemos su información personal. Podemos compartir información en las
              siguientes circunstancias:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li><strong>Con su consentimiento:</strong> cuando nos autoriza expresamente</li>
              <li><strong>Proveedores de servicios:</strong> empresas que nos ayudan a operar el Servicio
                (procesadores de pago, servicios de mensajería)</li>
              <li><strong>Requisitos legales:</strong> cuando sea requerido por ley o proceso legal</li>
              <li><strong>Protección de derechos:</strong> para proteger los derechos y seguridad de
                WashFlow, nuestros usuarios u otros</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">4. Seguridad de los Datos</h2>
            <p class="text-muted-foreground leading-relaxed">
              Implementamos medidas de seguridad técnicas y organizativas para proteger
              su información, incluyendo:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Encriptación de datos en tránsito y en reposo</li>
              <li>Acceso restringido a información personal</li>
              <li>Monitoreo continuo de seguridad</li>
              <li>Respaldos regulares de datos</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">5. Retención de Datos</h2>
            <p class="text-muted-foreground leading-relaxed">
              Conservamos su información mientras su cuenta esté activa o según sea necesario
              para proporcionarle servicios. Si desea eliminar su cuenta, puede solicitarlo
              contactándonos directamente. Algunos datos pueden retenerse por períodos más
              largos según lo requiera la ley.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">6. Sus Derechos</h2>
            <p class="text-muted-foreground leading-relaxed">
              De acuerdo con la Ley Federal de Protección de Datos Personales en Posesión
              de los Particulares (LFPDPPP), usted tiene derecho a:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li><strong>Acceso:</strong> conocer qué datos personales tenemos sobre usted</li>
              <li><strong>Rectificación:</strong> corregir datos inexactos o incompletos</li>
              <li><strong>Cancelación:</strong> solicitar la eliminación de sus datos</li>
              <li><strong>Oposición:</strong> oponerse al tratamiento de sus datos</li>
            </ul>
            <p class="text-muted-foreground leading-relaxed mt-2">
              Para ejercer estos derechos, contáctenos en
              <a href="mailto:privacidad@washflow.mx" class="text-primary hover:underline">
                privacidad@washflow.mx
              </a>
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">7. Cookies y Tecnologías Similares</h2>
            <p class="text-muted-foreground leading-relaxed">
              Utilizamos cookies y tecnologías similares para:
            </p>
            <ul class="list-disc list-inside text-muted-foreground space-y-2 ml-4">
              <li>Mantener su sesión iniciada</li>
              <li>Recordar sus preferencias</li>
              <li>Analizar el uso del Servicio</li>
              <li>Mejorar la experiencia del usuario</li>
            </ul>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">8. Menores de Edad</h2>
            <p class="text-muted-foreground leading-relaxed">
              Nuestro Servicio no está dirigido a menores de 18 años. No recopilamos
              intencionalmente información de menores. Si descubrimos que hemos recopilado
              información de un menor, la eliminaremos de inmediato.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">9. Cambios a esta Política</h2>
            <p class="text-muted-foreground leading-relaxed">
              Podemos actualizar esta Política de Privacidad periódicamente. Le notificaremos
              sobre cambios significativos publicando la nueva política en esta página y,
              cuando sea apropiado, enviándole una notificación por correo electrónico.
            </p>
          </section>

          <section class="space-y-4 mt-8">
            <h2 class="text-2xl font-semibold">10. Contacto</h2>
            <p class="text-muted-foreground leading-relaxed">
              Si tiene preguntas sobre esta Política de Privacidad o sobre cómo manejamos
              sus datos, puede contactarnos en:
            </p>
            <div class="text-muted-foreground mt-2 space-y-1">
              <p>
                <strong>Correo:</strong>
                <a href="mailto:privacidad@washflow.mx" class="text-primary hover:underline">
                  privacidad@washflow.mx
                </a>
              </p>
              <p>
                <strong>Asunto:</strong> Solicitud de Privacidad - WashFlow
              </p>
            </div>
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
              to="/terms"
              class="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Términos de Servicio
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
