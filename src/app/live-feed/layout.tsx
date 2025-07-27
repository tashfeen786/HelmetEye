
import type {Metadata} from 'next';

export const metadata: Metadata = {
  title: 'Live Feed | HelmetEye',
  description: 'Live feed for AI-Powered Helmet Detection and Safety Monitoring',
};

export default function LiveFeedLayout({
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
