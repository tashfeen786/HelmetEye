
import type {Metadata} from 'next';

export const metadata: Metadata = {
  title: 'Dashboard | HelmetEye',
  description: 'AI-Powered Helmet Detection and Safety Monitoring',
};

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
        {children}
    </>
  );
}
