# 🍺🍷 Bot e Microsite de Promoções de Cervejas e Vinhos (Sertãozinho)

Sistema completo com **Bot no Telegram (@beerstz_bot)**, **Robôs de Coleta (Savegnago, Mercado Livre, Amazon, Wine, Evino)**, **Histórico SQLite** e **Microsite no GitHub Pages**.

---

## 🌐 Como Ativar o GitHub Pages (Em 3 Passos)

1. Envie este repositório para a sua conta no GitHub (`git init`, `git add .`, `git commit -m "feat: inicial"`, `git push`).
2. No seu repositório no GitHub, acesse **Settings** > **Pages** (na barra lateral esquerda).
3. Na seção **Build and deployment** > **Branch**:
   * Selecione a branch `main` (ou `master`).
   * Selecione a pasta **`/docs`**.
   * Clique em **Save**.
4. Pronto! Seu site estará publicado gratuitamente em:
   `https://<seu-usuario>.github.io/<nome-do-repositorio>/`

---

## 🚀 Funcionalidades

- **🌐 Microsite Moderno & Responsivo (`/docs`):**
  - Painel com filtros de **Cervejas**, **Vinhos**, **Supermercados de Sertãozinho** e **Cupons**.
  - Barra de busca em tempo real com ordenação por maior desconto e menor preço.
  - Badges de frete rápido (Full, Prime e Delivery Local).
- **🤖 Robôs de Coleta Automática 4x ao dia (08h, 12h, 16h, 20h):**
  - *Savegnago Supermercados (Sertãozinho)*
  - *Mercado Livre (Mercado Envios Full)*
  - *Amazon Brasil (Prime)*
  - *Wine.com.br & Evino*
- **📱 Bot no Telegram ([@beerstz_bot](https://t.me/beerstz_bot)):**
  - Notificações automáticas com resumo das 4 rodadas diárias.
  - Alertas instantâneos de quedas de preço.
  - Botão interativo para abrir o microsite e pesquisar qualquer bebida.
- **🔄 GitHub Actions Automático (`.github/workflows/update-deals.yml`):**
  - Roda os scrapers automaticamente nos servidores do GitHub 4x por dia e atualiza o site no GitHub Pages sem custo!
