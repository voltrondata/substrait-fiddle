/// <reference types="cypress" />

describe('Substrait Fiddle Basic Test', ()=>{
    beforeEach(()=>{
        cy.visit('/')
    })


    it('header with title and logo', ()=>{
        cy.get('.navbar')
            .should("have.text", "Substrait Fiddle")
            .find("img").should("be.visible");
    })

    it('tabs for code and upload', ()=>{
        cy.contains('.tabs','Code')
        cy.contains('.tabs','Upload')
    })

    it('tabs should work for routing', ()=>{
        cy.get('button')
        .contains('Upload')
        .click()
        .url()
        .should('include','/upload')
        
        cy.get('button')
        .contains('Code')
        .click()
        .url()
        .should('not.include','/upload')
    })

    it('monaco editor should load', ()=>{
        cy.contains('Code')
        .click()
        .get("#editor")
        .type('{moveToEnd}')
        .contains('#editor', '{"_comment1": "Enter JSON to generate Substrait Plan"}')

        cy.get('#language')
        .select('sql')
        .get('#editor')
        .contains('#editor','-- Enter SQL query to generate Substrait Plan')
    })

})
