import './globals.css';

export const metadata = {
  title: 'Multi-Agent Orchestrator',
  description: 'A white-box software delivery dashboard driven by multiple AI agents.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
