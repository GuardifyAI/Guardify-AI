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
cd guardify-ui
npm install
npm run dev
```

npm install only in the first run
Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 3. Project Structure (Vite + React)

```
guardify-ui/
├── public/
│   └── images/         # logos, icons
│
├── src/
│   ├── App.tsx         # main UI
│   ├── main.tsx        # entry point
│   └── styles.css      # global styles
│
├── index.html
├── package.json
├── tsconfig.json
└── README.md
```

---

## 4. Tech Stack

- React (with TypeScript)
- Vite
- Chart.js (for graphs)
- CSS modules / custom styles

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
- Do not commit `node_modules/` or `.env` files
- Static assets like logos go in `public/images/`

---

For any questions or issues, contact **Ofek** 🎯
