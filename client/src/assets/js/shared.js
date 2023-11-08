import axios from "axios";
import * as jose from "jose";
import { SubstraitParser } from "./substrait-parser";
import { buildGraph, clearGraph, drawGraph } from "./substrait-d3";

function readText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

async function validate(plan, override_levels, status_func) {
  try {
    await axios.post("/api/route/validate/", {
      plan: plan,
      override_levels: override_levels,
    });
    status_func("Plan validation successful!");
  } catch (error) {
    status_func(error.response.data["detail"]);
  }
}

function plot(plan, status_func) {
  try {
    clearGraph();
    const subplan = new SubstraitParser(plan).planToNode(plan);
    const graph = buildGraph(subplan);
    drawGraph(graph["nodes"], graph["edges"]);
    status_func("Plan generation successful!");
  } catch (error) {
    status_func("Error generating plot: " + error);
  }
}

async function getPlan(id) {
  try {
    const hex = /^[0-9a-fA-F]+$/;
    if (!hex.test(id)) {
      alert("Invalid ID: ID contains non-hexadecimal elements");
      throw console.error("Invalid ID passed");
    }
    const response = await axios.post("/api/route/fetch/?id=" + id);
    return response;
  } catch (error) {
    console.error(error);
    if (error.response.status == 404) {
      alert(error.response.data["detail"]);
    }
  }
}

async function generateToken(user_id) {
  const payload = {
    user_id: user_id,
  };
  const secret = new TextEncoder().encode(process.env.SESSION_SECRET);
  const token = await new jose.SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .sign(secret);
  return token;
}

export {
  readFile,
  readText,
  validate,
  plot,
  clearGraph,
  getPlan,
  generateToken,
};
