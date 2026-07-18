import Image from "next/image";
import styles from "./BrandLogo.module.css";

export const SAHAAY_LOGO_SRC = "/sahaay logo.jpeg";

interface BrandLogoProps {
  className?: string;
  priority?: boolean;
}

export function BrandLogo({ className, priority = false }: BrandLogoProps) {
  return (
    <Image
      src={SAHAAY_LOGO_SRC}
      alt="Sahaay — AI-Powered Voice Health Monitoring"
      width={320}
      height={320}
      className={`${styles.logo} ${className ?? ""}`}
      priority={priority}
    />
  );
}
