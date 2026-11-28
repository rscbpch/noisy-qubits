import type { ButtonHTMLAttributes } from 'react'
import './Button.css'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export default function Button({ variant = 'secondary', type = 'button', ...rest }: Props) {
  return <button {...rest} type={type} className={`button button-${variant}`} />
}
