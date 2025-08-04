# Guardify UI – Team Setup Instructions

Follow these steps to set up the development environment and start working with the Guardify AI web interface.

---

## 1. Requirements

Make sure each team member has:

- [Node.js](https://nodejs.org/) installed (includes `npm`)
- A modern browser (e.g. Chrome)
- A code editor (preferably [Visual Studio Code](https://code.visualstudio.com/))

---

## 2. Run the project locally

```bash
cd UI/Guardify-UI
npm install
npm run dev
```

npm install only in the first run
Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 3. Project Structure (Vite + React)

```
Guardify-UI/
├── public/
│   └── images/         # logos, icons
│
├── src/
│   ├── components/     # UI components (Sidebar, EventCard, Stats)
│   ├── pages/          # LoginPage, EventPage, ShopPage
│   ├── context/        # EventsContext
│   ├── App.tsx         # main UI
│   ├── AppContent.tsx  # dashboard layout
│   ├── main.tsx        # entry point
│   ├── index.css       # global styles with Tailwind
│   ├── types.ts        # TypeScript definitions
│   └── events.ts       # sample data
│
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── package.json
├── tsconfig.json
└── README.md
```

---

## 4. Tech Stack

- React (with TypeScript)
- Vite
- Tailwind CSS (for styling)
- Lucide React (for icons)
- Chart.js (for graphs)
- React Router (for navigation)

---

## 5. Common Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview built version
```

---

## 🧠 Notes

- All UI logic is in `src/`
- Tailwind CSS v3.4 is configured for styling
- Demo login: `guardifyai@gmail.com` / `1234`
- Do not commit `node_modules/` or `.env` files
- Static assets like logos go in `public/images/`

---

For any questions or issues, contact **Ofek** 🎯
