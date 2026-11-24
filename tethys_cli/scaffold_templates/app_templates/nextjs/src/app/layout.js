import './globals.css';
import AppShell from '@/components/AppShell';

export const metadata = {
  title: process.env.NEXT_PUBLIC_TETHYS_APP_NAME,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
