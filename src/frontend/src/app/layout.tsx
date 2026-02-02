import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Treasury Management System',
    description: 'Thai Commercial Bank Treasury Operations - Bond Trading, Interbank, Repo',
    keywords: ['treasury', 'bond', 'trading', 'repo', 'interbank', 'ThaiBMA'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className="min-h-screen bg-gray-50 dark:bg-gray-900 antialiased">
                {children}
            </body>
        </html>
    );
}
