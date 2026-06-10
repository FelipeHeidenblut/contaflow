/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#19341a', // Verde Escuro (Confiança/Estabilidade)
          coral: '#ff8a65', // Coral (CTAs e Destaques)
          text: '#2a2a2a', // Cinza Chumbo (Texto Principal)
          bg: '#f8f8f8', // Off-White (Fundo Geral)
        },
      },
    },
  },
  plugins: [],
}
