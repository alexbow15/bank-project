import React from "react";
import "./button.css";

interface Props {
  onClick: () => void;
  label: string;
  color: string;
}

const Button: React.FC<Props> = ({ onClick, label, color }) => {
  return (
    <button onClick={onClick} className={"btn btn-" + color}>
      {label}
    </button>
  );
};

export default Button;
