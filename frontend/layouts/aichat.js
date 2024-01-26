import Head from "next/head"
import Image from "next/image"
import Link from "next/link"

import { useRouter } from "next/router"
import { useState, useEffect } from "react"

import { Nav } from "react-bootstrap"
import { Button } from "react-bootstrap"
import { Modal } from "react-bootstrap"
import { Form } from "react-bootstrap"

import { produce } from "immer"

import service from "../service";

import styles from "../styles/AIChat.module.css";

export default function AIChatLayout({ children }) {
  const router = useRouter();

  let { pathname, parserId, documentId, pageNum } = router.query;

  const [parser, setParser] = useState(null)

  const [parserDocuments, setParserDocuments] = useState([])

  const [changeDocumentModal, setChangeDocumentModal] = useState({
    show: false
  })

  const getParser = () => {
    if (!parserId) return
    service.get("parsers/" + parserId + "/", (response) => {
      setParser(response.data)
    })
  }

  const getParserDocuments = () => {
    if (!parserId) return
    service.get("documents/?parserId=" + parserId, response => {
      let parserDocuments = response.data
      for (let j=0; j<parserDocuments.length; j++) {
        let pd = parserDocuments[j]
        let ocredPagesCount = 0
        for (let i=0 ;i<pd.documentPages.length; i++) {
          if (pd.documentPages[i].ocred) {
            ocredPagesCount += 1
          }
        }
        pd.ocredPagesCount = ocredPagesCount
        pd.name = pd.filenameWithoutExtension + "." + pd.extension + " (Page " + ocredPagesCount + " of " + pd.totalPageNum + ")"
      }
      setParserDocuments(parserDocuments)
    })
  }

  const changeDocumentModalOpenHandler = () => {
    setChangeDocumentModal(produce(draft => {
      draft.show = true
    }))
  }

  const changeDocumentModalCloseHandler = () => {
    setChangeDocumentModal(produce(draft => {
      draft.show = false
    }))
  }

  const selectedDocumentChangeHandler = (e) => {
    router.push({
      pathname,
      query: {
        ...router.query,
        documentId: e.target.value,
        pageNum: 1
      },
    })
  }

  useEffect(() => {
    getParser()
    getParserDocuments()
  }, [parserId])

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.wrapper}>
        <header className={styles.header}>
          <div>
            <div className="row" style={{ padding: 0, margin: 0 }}>
              <div
                className="col-4 col-md-4"
                style={{ paddingLeft: 20, paddingRight: 0 }}
              >
                <div className={styles.logoDiv}>
                  <Image
                    src="/static/img/logo.png"
                    width="40"
                    height="36"
                    alt="Cashew Docparser"
                  />
                </div>
                <h2>Cashew</h2>
                &nbsp;&nbsp;&nbsp;
                <Nav.Link
                  href="/workspace/parsers"
                  style={{ display: "inline-block", verticalAlign: "top" }}
                >
                  <i
                    className={
                      styles.parsersIcon + " bi bi-grid"
                    }
                  ></i>
                </Nav.Link>
                <div style={{ display: "inline-block", verticalAlign: "text-bottom", marginLeft: 10 }}>
                  <Button onClick={() => router.push("/workspace/parsers/" + parserId + "/rules")}>Back to Configurations</Button>
                </div>
              </div>
              <div
                className="col-4 col-md-4"
                style={{ paddingLeft: 0, paddingRight: 20, width: "100%", textAlign: "center" }}
              >
                {parserDocuments && documentId && (
                  <>123
                    {parserDocuments.find(d => d.id == documentId).filenameWithoutExtension + "." + parserDocuments.find(d => d.id == documentId).extension}
                  </>
                )}
              </div>
              <div
                className="col-4 col-md-4"
                style={{ paddingLeft: 0, paddingRight: 20 }}
              >
                <nav className={styles.nav}>
                  <ul>
                    <li>
                      <Button className="btn" onClick={changeDocumentModalOpenHandler}>
                        Change Document
                      </Button>
                      <Modal show={changeDocumentModal.show} onHide={changeDocumentModalCloseHandler}>
                        <Modal.Header closeButton>
                          <Modal.Title>Change Document</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                          <Form.Group className="mb-3" controlId="formRuleType">
                            <Form.Select aria-label="Document" onChange={selectedDocumentChangeHandler} value={documentId}>
                              <option value=""></option>
                              {parserDocuments && parserDocuments.map(parserDocument => (
                                <option key={parserDocument.id} value={parserDocument.id}>{parserDocument.name}</option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Modal.Body>
                        <Modal.Footer>
                          <Button variant="primary" onClick={changeDocumentModalCloseHandler}>
                            Confirm
                          </Button>
                          <Button variant="secondary" onClick={changeDocumentModalCloseHandler}>
                            Close
                          </Button>
                        </Modal.Footer>
                      </Modal>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <>
          {children}
        </>
        <footer className={styles.footer}>
          <div style={{ width: "100%", padding: "0 10px" }}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm" style={{ padding: "10px" }}>
                <div className={styles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
