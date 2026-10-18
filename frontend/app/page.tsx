import InquiryForm from './ui/InquiryForm';
type Service={id:number;title:string;slug:string;category:string;description:string;price_from:string|null;currency:string};
type Opportunity={id:number;title:string;country:string;description:string;employer:string;vacancies:number;deadline:string|null};
const base=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const internalBase=process.env.API_INTERNAL_URL || base;
async function fetchItems<T>(endpoint:string):Promise<T[]>{
 try {const r=await fetch(`${internalBase}/public/ehan-international/${endpoint}/`,{next:{revalidate:60}});if(!r.ok)return [];const json=await r.json();return Array.isArray(json)?json:(json.results??[])}catch{return []}
}
export default async function Home(){
 const [services,opportunities]=await Promise.all([fetchItems<Service>('services'),fetchItems<Opportunity>('opportunities')]);
 return <>
 <header><div className="wrap nav"><a className="brand" href="/">Ehan International Ltd</a><nav className="links" aria-label="Main navigation"><a href="#services">Services</a><a href="#opportunities">Opportunities</a><a href="#about">About</a><a href="#contact">Contact</a></nav></div></header>
 <main><section className="hero"><div className="wrap"><div className="eyebrow">Recruitment · Travel · Visa Services</div><h1>Professional support for work, travel and new opportunities.</h1><p>Explore our services and speak with our team about the documents, eligibility and procedures that apply to your plans.</p><a className="btn" href="#contact">Make an inquiry</a></div></section>
 <section className="section" id="services"><div className="wrap"><h2>Our services</h2><p className="sub">Specialized support for individuals, families and businesses.</p><div className="cards">{services.length?services.map(s=><article className="card" key={s.id}><span className="pill">{s.category}</span><h3>{s.title}</h3><p>{s.description}</p>{s.price_from&&<p>Starting from {s.currency} {s.price_from}</p>}</article>):<p>Our service catalog is being updated. Contact us for details.</p>}</div></div></section>
 <section className="section" style={{background:'#f0f4f0'}} id="opportunities"><div className="wrap"><h2>Recruitment opportunities</h2><p className="sub">Only reviewed opportunities are shown here. Employment and visa approval are not guaranteed.</p><div className="cards">{opportunities.length?opportunities.map(o=><article className="card" key={o.id}><span className="pill">{o.country}</span><h3>{o.title}</h3><p>{o.description}</p><p>Vacancies: {o.vacancies}{o.deadline?` · Apply by ${o.deadline}`:''}</p></article>):<p>No recruitment opportunities are currently published.</p>}</div></div></section>
 <section className="section" id="about"><div className="wrap"><h2>Clear information. Responsible service.</h2><p className="sub">Our team helps clients understand available services, documentation and next steps. Any government approval is determined by the responsible authority.</p></div></section>
 <section className="section" id="contact"><div className="wrap split"><div><h2>Contact our team</h2><p className="muted">Tell us what you need. We will review your inquiry and respond through the contact information you provide.</p><p className="muted">Do not submit passport scans, payment details or sensitive personal information through this general inquiry form.</p></div><InquiryForm apiBase={base}/></div></section></main>
 <footer><div className="wrap">© {new Date().getFullYear()} Ehan International Ltd. All rights reserved. Service availability and eligibility are subject to verification.</div></footer>
 </>
}
