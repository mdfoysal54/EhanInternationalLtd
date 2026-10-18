import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {title:'Ehan International Ltd | Recruitment, Travel & Visa Services',description:'Explore recruitment, travel, visa, Hajj, Umrah and education consultancy services.'};
export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
