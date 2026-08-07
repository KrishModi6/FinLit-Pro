import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

/**
 * ESLint flat config.
 *
 * This exists because two real bugs shipped that a linter would have caught
 * for free: a `useEffect` that fetched without a cleanup guard, so a slow
 * response could overwrite a newer one, and imports left behind after a
 * refactor. Both are single rules below.
 *
 * Three environments, because the code runs in three places:
 *   - src/**      the browser (React, JSX, DOM globals)
 *   - api/**      Vercel's Node runtime (process, no DOM)
 *   - *.config.js and scripts/**  Node at build time
 */
export default [
  { ignores: ['dist/**', 'node_modules/**', 'public/**'] },

  // ---- Browser code -------------------------------------------------------
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    settings: { react: { version: 'detect' } },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.flat.recommended.rules,
      ...react.configs.flat['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,

      // The two rules this config exists for, both as errors so the clean
      // state they are in now cannot quietly rot.
      'react-hooks/exhaustive-deps': 'error',
      // `caughtErrors: none` keeps bare `catch {}` quiet, which this codebase
      // uses deliberately for optional localStorage writes.
      'no-unused-vars': ['error', { caughtErrors: 'none', argsIgnorePattern: '^_' }],

      // ---- Deliberately off, with reasons ---------------------------------

      // Prop types are not used anywhere here; the components are small and
      // local. Off rather than annotating 84 files for no runtime benefit.
      'react/prop-types': 'off',

      // Flagged 24 apostrophes and quotation marks inside lesson prose. They
      // are valid JSX text and render correctly. This is a course whose whole
      // product is English sentences, and `&rsquo;` littered through them
      // would make the content materially harder to write and proofread.
      'react/no-unescaped-entities': 'off',

      // Flagged SimUI (exports money/num/pct beside its components) and the
      // two context files (export their hooks beside their providers). Those
      // pairings are intentional, and the rule is about dev-server hot reload
      // rather than anything a reader ever sees.
      'react-refresh/only-export-components': 'off',

      // Flagged seven effects that set state synchronously. Every one is a
      // genuine external-sync effect: reading saved progress out of
      // localStorage on mount, resetting quiz state when the lesson changes,
      // and raising the loading flag before a fetch. The cost is one extra
      // render each, and the alternatives are worse than the warning. Left
      // off rather than as a warning nobody will ever clear.
      'react-hooks/set-state-in-effect': 'off',

      // Flagged `const Content = getContent(mod.id)` in ModulePage. Checked:
      // getContent is a lookup into a module-level registry of lazy()
      // components with a module-level fallback, so the component identity is
      // stable across renders and the lesson does not remount. The rule
      // cannot prove that from the call site.
      'react-hooks/static-components': 'off',
    },
  },

  // ---- Serverless functions ----------------------------------------------
  {
    files: ['api/**/*.js'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: { ...globals.node, fetch: 'readonly', AbortSignal: 'readonly' },
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-unused-vars': ['error', { caughtErrors: 'none', argsIgnorePattern: '^_' }],
    },
  },

  // ---- Build-time Node ----------------------------------------------------
  {
    files: ['*.config.js', 'scripts/**/*.mjs', 'vite.config.js'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: globals.node,
    },
    rules: { ...js.configs.recommended.rules },
  },
]
