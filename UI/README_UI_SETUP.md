# Guardify UI – Team Setup Instructions
Follow these steps to set up the development environment and start working with TypeScript and the web interface.


## 1. Requirements

Make sure each team member has:

- [Node.js](https://nodejs.org/) installed (includes `npm`)
- A modern browser (e.g. Chrome)
- A code editor (preferably [Visual Studio Code](https://code.visualstudio.com/))


## 2. Install TypeScript locally

```bash
npm install typescript --save-dev
```

To verify:
```bash
npx tsc -v
```

## 3. Compile TypeScript

### One-time compilation:
```bash
npx tsc
```

### Recommended: Auto-compile on save (watch mode):
```bash
npx tsc --watch
```

This will recompile any changed `.ts` file into `js/`.


## 4. Recommended VS Code Extensions

- **Live Server** (to view `index.html` in browser with live reload)
- **Run on Save** (optional – to run `tsc` automatically when saving `.ts` files)


## 5. Project Structure

```
ui/
├── index.html
├── styles.css
├── ts/            ← TypeScript code goes here
│   └── main.ts
├── js/            ← Compiled JavaScript will be placed here
│   └── main.js
├── images/
└── tsconfig.json
```


## 6. tsconfig.json

Your config should look like:

```json
{
  "compilerOptions": {
    "target": "es2016",
    "module": "es6",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "rootDir": "./ts",
    "outDir": "./js"
  },
  "include": ["ts/**/*"]
}
```

## 7. Run the project

Open `index.html` in your browser (or use Live Server).  
Try switching between shops – the dashboard should update.