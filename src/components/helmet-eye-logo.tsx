import type { SVGProps } from 'react';

export function HelmetEyeLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M12 2a9 9 0 0 0-9 9v5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a9 9 0 0 0-9-9z" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  );
}
