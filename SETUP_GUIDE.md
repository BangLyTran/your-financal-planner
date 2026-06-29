# Financial Planner Cloud Sync Setup

This package is already coded for:

- local-first/offline storage
- Google OAuth sign-in
- Apple OAuth sign-in
- passwordless email-link sign-in fallback
- one private cloud planner document per user
- automatic upload after edits
- automatic cloud checks on app focus and every 30 seconds
- manual **Sync now**, **Use cloud copy**, and **Upload this device** controls
- installable web-app metadata for iOS, iPadOS, macOS, and Windows

## 1. Create the Supabase project

1. Create a project in Supabase.
2. Open **Project Settings > API**.
3. Copy:
   - Project URL
   - Publishable key (`sb_publishable_...`) or legacy anon key
4. Do **not** use the `service_role` key.
5. Open `cloud-config.js` and replace the two placeholder values.

## 2. Create the private cloud table

1. In Supabase, open **SQL Editor**.
2. Paste and run all of `supabase_schema.sql`.
3. Confirm `public.financial_plans` exists.
4. Confirm Row Level Security is enabled.

The policies only permit an authenticated user to access the row whose `user_id` equals their own Supabase Auth user ID.

## 3. Deploy the folder to an HTTPS address

OAuth will not work when `index.html` is opened as a `file://` URL.

The easiest path is a static host such as Netlify:

1. Keep `index.html`, `cloud-config.js`, `manifest.webmanifest`, `service-worker.js`, and the `icons` folder together.
2. Drag only the `DEPLOY_THIS_FOLDER` folder into Netlify Drop.
3. Copy the resulting production URL, for example:
   `https://your-financial-planner.netlify.app/`

GitHub Pages, Cloudflare Pages, and Vercel also work.

The deploy folder contains no salary, debt, bill, or vehicle values. Your preloaded plan is kept in the separate private JSON file so those details do not become visible in the public website source.

## 4. Configure the Supabase app URL

In Supabase, open **Authentication > URL Configuration**:

- Site URL: your exact production URL
- Redirect URLs: add the exact production URL

Example:

- `https://your-financial-planner.netlify.app/`

The app sends OAuth users back to its current path, so the allow-list entry must match that deployed URL.

## 5. Fastest first login: email link (no Google/Apple setup required)

After the project, SQL, and HTTPS deployment are ready, Supabase email authentication normally works without configuring a social provider:

1. Open the deployed planner.
2. Go to **Settings > Cloud sync and sign-in**.
3. Enter your email and choose **Email me a sign-in link**.
4. Open the link in the email.

This is the fastest way to verify cross-device synchronization. Google and Apple buttons can be enabled afterward.

## 6. Enable Sign in with Google

1. In Google Cloud, create an OAuth client of type **Web application**.
2. Authorized JavaScript origin:
   `https://your-financial-planner.netlify.app`
3. Authorized redirect URI:
   `https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`
4. Copy the Google Client ID and Client Secret.
5. In Supabase, open **Authentication > Providers > Google**.
6. Enable Google and paste the Client ID and Client Secret.

## 7. Enable Sign in with Apple

This requires an Apple Developer account.

1. Create or use an Apple **App ID** with the **Sign in with Apple** capability.
2. Create a **Services ID** for the web app.
3. Configure the Services ID website domain as:
   `YOUR_PROJECT_REF.supabase.co`
4. Configure its return URL as:
   `https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`
5. Create a Sign in with Apple key and securely retain the downloaded `.p8` file.
6. Generate the Apple OAuth client secret.
7. In Supabase, open **Authentication > Providers > Apple**.
8. Enable Apple and enter the Services ID and generated secret.
9. Rotate the Apple OAuth secret at least every six months.

## 8. First private-data sync

1. Open the deployed planner.
2. Go to **Settings > Cloud sync and sign-in**.
3. Sign in with Google, Apple, or the email-link fallback.
4. Go to **Settings > Data controls** and import `bang_private_financial_plan.json` from the separate `PRIVATE_DO_NOT_UPLOAD` folder.
5. The imported plan saves locally and uploads automatically. You can also choose **Upload this device**.
6. On every additional device, open the same deployed URL and use the same account; the cloud plan downloads automatically.

Never upload the `PRIVATE_DO_NOT_UPLOAD` folder or its JSON file to a public static host.

Use the same provider consistently. If Apple Hide My Email produces a relay address different from your Google email, Supabase may treat it as a separate account with a separate planner row.

## 9. Install on each device

- **iPhone/iPad:** Safari > Share > Add to Home Screen
- **macOS:** Safari > File > Add to Dock, or use Chrome/Edge install controls
- **Windows:** Chrome/Edge > Install app

## Conflict behavior

- Normal edits upload after about 1.2 seconds.
- The app checks the cloud whenever it regains focus and every 30 seconds while visible.
- If two devices edit before seeing each other’s changes, the newest timestamp wins.
- Export a JSON backup before manually choosing **Use cloud copy** or **Upload this device**.

## Security model

- Browser sessions are handled by Supabase Auth.
- Financial data is sent over HTTPS.
- Row Level Security limits each user to their own row.
- The cloud document is not end-to-end encrypted; the Supabase project owner can access the database.
- Keep the Supabase account protected with multi-factor authentication.


## What cannot be automated from this package

The remaining account-owner actions cannot be safely performed by the app or by another person:

- accepting Supabase project terms and owning its billing/security settings
- creating Google OAuth credentials and entering the Google client secret in Supabase
- creating Apple identifiers/keys and entering the Apple secret in Supabase
- choosing and controlling the final HTTPS domain

Do not send Google client secrets, Apple `.p8` keys, Apple private keys, or Supabase service-role keys through chat. The Supabase project URL and publishable/anon key are public browser configuration and can be embedded in `cloud-config.js`.
