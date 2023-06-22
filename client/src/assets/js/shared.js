import axios from "axios";
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
    await axios.post("/api/validate/", {
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

async function getPlan(id){
  try {
    console.log("id: ", id)
    const response = await axios.post("/api/fetchplan/?id="+id);
    return response;
  } catch (error) {
    console.log(error);
  }
}

export { readFile, readText, validate, plot, clearGraph, getPlan };
