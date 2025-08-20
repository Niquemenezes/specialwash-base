import React from "react";
import CardProductos from "../components/CardProductos";
export default function PrivateAdmin(){
  return(<div className="container py-4">
    <h2 className="mb-4">Panel Administrador</h2>
    <div className="row"><div className="col-12"><CardProductos/></div></div>
  </div>);
}
