/// <reference types="cypress" />

describe("Substrait Fiddle Custom Schema test", () => {
  
    it("add custom schema", { browser: 'electron' }, () => {
      cy.visit("/")

      cy.get("select").select("sql");

      cy.get("button").contains("Show/Add Schema").click();
      
      cy.get("#addSchema").click();

      cy.get("#schemaModal")
      .focused()
      .contains("New Schema")
    
      cy.get("#schemaTextArea")
      .type(`
        {
            "table": "test",
            "fields": [
            {
                "name": "field_1",
                "type": "INTEGER",
                "properties": [
                "NOT NULL"
                ]
            }
        ]
        }
      `);

      cy.get("button").contains("Validate").click();
      cy.on('window:alert', (str) => {
        expect(str).to.equal(`Schema validated!`);
      });

      cy.get("button").contains("Save changes").click();

      cy.get("#editor")
      .click()
      .focused()
      .type("{ctrl}a")
      .clear()
      .type("select * from test;");

      cy.get("button").contains("Generate").click();

      cy.get("#status").should("contain", "Plan generation successful!");

      cy.get("svg").should("not.be.empty");

    });

    it("schema for lineitem table", { browser: 'electron' }, () => {
      cy.visit("/")

      cy.get("select").select("sql");

      cy.get("button").contains("Show/Add Schema").click();
      
      cy.get("#addSchema").click();

      cy.get("#schemaModal")
      .focused()
      .contains("New Schema")
    
      cy.get("#schemaTextArea")
      .type(`
        {
            "table": "lineitem",
            "fields": [
            {
                "name": "field_1",
                "type": "INTEGER",
                "properties": [
                "NOT NULL"
                ]
            }
        ]
        }
      `);

      cy.get("button").contains("Validate").click();
      cy.on('window:alert', (str) => {
        expect(str).to.equal(`Invalid schema: Table name cannot be "lineitem"`);
      });

    });

    it("schema with invalid format", { browser: 'electron' }, () => {
      cy.visit("/")

      cy.get("select").select("sql");

      cy.get("button").contains("Show/Add Schema").click();
      
      cy.get("#addSchema").click();

      cy.get("#schemaModal")
      .focused()
      .contains("New Schema")
    
      cy.get("#schemaTextArea")
      .type(`
        {
            "table": "lineitem",
            "field": [
            {
                "name": "field_1",
                "type": "INTEGER",
            }
        ]
        }
      `);

      cy.get("button").contains("Validate").click();
      cy.on('window:alert', (str) => {
        expect(str).to.contain(`Invalid JSON: SyntaxError:`);
      });

    });

  });
  