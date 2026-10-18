'use client';
import {useState, type FormEvent} from 'react';
export default function InquiryForm({apiBase}:{apiBase:string}){
 const [state,setState]=useState<'idle'|'sending'|'done'|'error'>('idle');
 async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();setState('sending');const form=e.currentTarget;const fd=new FormData(form);
  const payload={name:String(fd.get('name')||''),email:String(fd.get('email')||''),phone:String(fd.get('phone')||''),message:String(fd.get('message')||''),consent:fd.get('consent')==='on'};
  try{const r=await fetch(`${apiBase}/public/ehan-international/inquiries/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!r.ok)throw new Error('Failed');form.reset();setState('done')}catch{setState('error')}
 }
 return <form className="form" onSubmit={submit}><label className="field">Full name<input name="name" maxLength={150} required autoComplete="name"/></label><label className="field">Phone<input name="phone" maxLength={35} required autoComplete="tel"/></label><label className="field">Email (optional)<input name="email" type="email" autoComplete="email"/></label><label className="field">How can we help?<textarea name="message" maxLength={3000} required/></label><label style={{display:'flex',gap:10,fontSize:13,marginBottom:20}}><input name="consent" type="checkbox" required/>I agree to be contacted about my inquiry.</label><button className="btn" type="submit" disabled={state==='sending'}>{state==='sending'?'Sending...':'Send inquiry'}</button>{state==='done'&&<p className="notice" role="status">Thank you. Your inquiry was received.</p>}{state==='error'&&<p className="notice" role="alert">Could not send your inquiry. Please try again later.</p>}</form>
}
