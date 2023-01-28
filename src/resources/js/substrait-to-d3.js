"use strict";

const { SubstraitParser } = require("./substrait-parser");
const d3 = require("d3");

// Populating map with nodes information
function createNodeIdToNodeMap(plan, nodes) {
  nodes.set(plan.id, plan);
  for (let i = 0; i < plan.inputs.length; ++i) {
    createNodeIdToNodeMap(plan.inputs[i], nodes);
  }
}

// Building graph from Substrait Plan
function buildGraph(plan) {
  let nodes = new Map();
  createNodeIdToNodeMap(plan.inputs[0], nodes);
  let edges = [];
  nodes.forEach((value) => {
    for (let i = 0; i < value.inputs.length; ++i) {
      edges.push({ source: value.inputs[i].id, target: value.id });
    }
  });
  return {
    nodes: nodes,
    edges: edges,
  };
}

// Processing nodes for d3JS forcedSimulation's format
function processNodes(nodes) {
  let processedNodes = [];
  nodes.forEach((value) => {
    processedNodes.push({ name: value.id, type: value.type });
  });
  return processedNodes;
}

// Processing edges for d3JS forcedSimulation's format
function processEdges(nodes, links) {
  let processedLinks = [];
  for (let i = 0; i < links.length; ++i) {
    let source = nodes.findIndex((j) => j.name === links[i].source);
    let target = nodes.findIndex((j) => j.name === links[i].target);
    processedLinks.push({ source, target });
  }
  return processedLinks;
}

// Specifying color of graph nodes
const COLORS = {
  "node-green": "#0E4D05",
  "node-blue": "#052748",
  "node-brown": "#4D2205",
  "node-purple": "#46054D",
};
function nodeColor(nodeType) {
  switch (nodeType) {
    case "sink":
      return COLORS["node-brown"];
    case "project":
      return COLORS["node-green"];
    case "read":
      return COLORS["node-blue"];
    case "join":
      return COLORS["node-purple"];
  }
}

// Specifying Font-Awesome icons for graph nodes
function nodeIcon(nodeType) {
  switch (nodeType) {
    case "sink":
      return "bi-download";
    case "project":
      return "bi-kanban";
    case "read":
      return "bi-eye";
    case "join":
      return "bi-sign-intersection-y";
  }
}

function typeToLabel(nodeType) {
  return nodeType[0].toUpperCase() + nodeType.substring(1);
}

// Drawing Graph using d3JS
function drawGraph(pre_nodes, pre_links, use_drag = true) {
  let width = 960,
    height = 375;
  let nodes = processNodes(pre_nodes);
  let links = processEdges(nodes, pre_links);

  // Instantiating a Force Simulation
  var force = d3
    .forceSimulation(nodes)
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("link", d3.forceLink().links(links))
    .force(
      "collide",
      d3.forceCollide((d) => 55)
    );

  var svg = d3
    .select("svg")
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 960 375");

  // For arrowheads in edges
  svg
    .append("defs")
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "-0 -5 10 10")
    .attr("refX", 27)
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 13)
    .attr("markerHeight", 13)
    .attr("xoverflow", "visible")
    .append("svg:path")
    .attr("d", "M 0,-5 L 10 ,0 L 0,5")
    .attr("fill", "black")
    .style("stroke", "none");

  // specifying links in the graph
  const link = svg
    .append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("marker-end", "url(#arrowhead)")
    .style("stroke", "black");

  // specifying nodes in graph
  const node = svg.append("g").selectAll("g").data(nodes).join("g");

  // specifying node shape and color
  node
    .append("circle")
    .attr("r", 25)
    .style("fill", (d) => {
      return nodeColor(d.type);
    })
    .style("stroke-opacity", 0.3);

  // adding icon in node
  node
    .append("svg:foreignObject")
    .attr("width", 50)
    .attr("height", 50)
    .attr("x", -7)
    .attr("y", -15)
    .style("color", "white")
    .html(function (d) {
      return '<i class="bi ' + nodeIcon(d.type) + '"></i>';
    });

  // displaying node data on click
  node.on("click", function (d) {
    let node = document.getElementById("nodeData");
    let nodeData = pre_nodes.get(d["currentTarget"]["__data__"]["name"]);
    node.innerHTML = "<h3>" + typeToLabel(nodeData.type) + " Node</h3>";
    node.innerHTML += "<h5>Node Name:" + nodeData.id + "</h5>";

    if (nodeData.inputs.length) {
      node.innerHTML += "<b>Inputs:</b> ";
      for (let i = 0; i < nodeData.inputs.length; ++i) {
        node.innerHTML += nodeData.inputs[i].id + ", ";
      }
      node.innerHTML = node.innerHTML.substring(0, node.innerHTML.length - 2);
    }

    if (nodeData.props.length) {
      node.innerHTML += "<br><br>";
      var propsTable = document.createElement("table");
      var propsTableHead = document.createElement("thead");
      var propsTableBody = document.createElement("tbody");
      var propsTableCaption = document.createElement("caption");
      propsTableCaption.innerHTML = "Properties";
      propsTable.appendChild(propsTableCaption);
      propsTable.appendChild(propsTableHead);
      propsTable.appendChild(propsTableBody);

      let row = document.createElement("tr");
      let heading_1 = document.createElement("th");
      let heading_2 = document.createElement("th");
      heading_1.innerHTML = "Name";
      heading_2.innerHTML = "Value";
      row.appendChild(heading_1);
      row.appendChild(heading_2);
      propsTableHead.append(row);

      for (let i = 0; i < nodeData.props.length; ++i) {
        row = document.createElement("tr");
        let data_1 = document.createElement("td");
        let data_2 = document.createElement("td");
        data_1.innerHTML = nodeData.props[i].name;
        data_2.innerHTML = nodeData.props[i].value;
        row.appendChild(data_1);
        row.appendChild(data_2);
        propsTableBody.appendChild(row);
      }
      node.appendChild(propsTable);
    }

    if (nodeData.schema.children.length) {
      node.innerHTML += "<br>";
      var childrenTable = document.createElement("table");
      var childrenTableHead = document.createElement("thead");
      var childrenTableBody = document.createElement("tbody");
      var childrenTableCaption = document.createElement("caption");
      childrenTableCaption.innerHTML = "Output Schema";
      childrenTable.appendChild(childrenTableCaption);
      childrenTable.appendChild(childrenTableHead);
      childrenTable.appendChild(childrenTableBody);

      let row = document.createElement("tr");
      let heading_1 = document.createElement("th");
      let heading_2 = document.createElement("th");
      let heading_3 = document.createElement("th");
      heading_1.innerHTML = "Name";
      heading_2.innerHTML = "Type";
      heading_3.innerHTML = "Nullability";
      row.appendChild(heading_1);
      row.appendChild(heading_2);
      row.appendChild(heading_3);
      childrenTableHead.append(row);

      for (let i = 0; i < nodeData.schema.children.length; ++i) {
        row = document.createElement("tr");
        let data_1 = document.createElement("td");
        let data_2 = document.createElement("td");
        let data_3 = document.createElement("td");
        data_1.innerHTML = nodeData.schema.children[i].name;
        data_2.innerHTML = nodeData.schema.children[i].type;
        data_3.innerHTML = nodeData.schema.children[i].nullability;
        row.appendChild(data_1);
        row.appendChild(data_2);
        row.appendChild(data_3);
        childrenTableBody.appendChild(row);
      }
      node.appendChild(childrenTable);
    }
  });

  // specifying on tick function for the graph
  force.on("tick", () => {
    link.attr("d", (d) => {
      return (
        "M" +
        d.source.x +
        "," +
        d.source.y +
        "A0,0 0 0,1" +
        d.target.x +
        "," +
        d.target.y
      );
    });
    node.attr("transform", (d) => `translate(${d.x},${d.y})`);
  });

  // network drag simulation
  function drag(network) {
    function dragstarted(event, d) {
      if (!event.active) network.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) network.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return d3
      .drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }

  if (use_drag) {
    node.call(drag(force));
  }

  // for legend mentioning node icons
  const nodeSet = new Set();
  for (let i = 0; i < nodes.length; ++i) {
    nodeSet.add(nodes[i].type);
  }

  var legend = svg
    .selectAll(".legend")
    .data(nodeSet)
    .enter()
    .append("g")
    .attr("class", "legend")
    .attr("transform", function (d, i) {
      return "translate(0," + i * 30 + ")";
    });

  legend
    .append("rect")
    .attr("x", -2)
    .attr("width", 50)
    .attr("height", 50)
    .style("fill", "transparent");

  legend
    .append("svg:foreignObject")
    .attr("width", 100)
    .attr("height", 100)
    .attr("y", -4)
    .style("color", "black")
    .html(function (d) {
      return '<i class="bi ' + nodeIcon(d) + '"></i>' + " " + d;
    });
}

module.exports = {
  buildGraph,
  drawGraph,
};
