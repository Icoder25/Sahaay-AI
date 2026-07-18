import { SahaayDemo } from "@/components/SahaayDemo/SahaayDemo";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <SahaayDemo />
    </div>
  );
}
