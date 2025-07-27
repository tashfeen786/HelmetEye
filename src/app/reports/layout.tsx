
import type {Metadata} from 'next';

export const metadata: Metadata = {
  title: 'Reports | HelmetEye',
  description: 'View detection reports on HelmetEye',
};

export default function ReportsLayout({
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
