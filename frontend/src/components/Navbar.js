import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav style={{
      backgroundColor: "#1e293b", // slate-800
      padding: "12px 24px",
      display: "flex",
      justifyContent: "start",
      gap: "16px",
      borderBottom: "2px solid #0f172a" // slate-900
    }}>
      {[
        { label: "Component Generator", path: "/" },
        { label: "Project Generator", path: "/project" },
        { label: "EDS Block Generator", path: "/eds-block-generator" }
      ].map((item) => (
        <Link
          key={item.path}
          to={item.path}
          style={{
            color: "white",
            textDecoration: "none",
            padding: "8px 12px",
            borderRadius: "6px",
            transition: "background 0.3s",
          }}
          onMouseOver={(e) => (e.target.style.background = "#334155")} // hover: slate-700
          onMouseOut={(e) => (e.target.style.background = "transparent")}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
};

export default Navbar;
