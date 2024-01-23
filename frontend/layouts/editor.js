import Head from 'next/head'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/router'

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Dropdown from 'react-bootstrap/Dropdown'
import { ToastContainer, Toast } from 'react-bootstrap'

import styles from '../styles/Editor.module.css'
import { useState, useEffect } from 'react'

import service from '../service'

export default function EditorLayout({ children }) {

  const router = useRouter()
  const { parserId, ruleId, documentId=0, pageNum=1, editorType="ruleProperties" } = router.query

  const [rules, setRules] = useState([])
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState("")
  const [openSidebar, setOpenSidebar] = useState(true)

  const getRulesByParserId = () => {
    if (parserId == undefined) return
    service.get("rules/?parserId=" + parserId, response => {
      setRules(response.data)
    })
  }

  const toggleSidebarHandler = () => {
    setOpenSidebar(!openSidebar)
  }

  useEffect(() => {
    getRulesByParserId()
  }, [router.isReady, parserId])

  const liRuleClickHandler = (e, rule) => {
    if (rule.ruleType == "INPUT_TEXTFIELD" || rule.ruleType == "INPUT_DROPDOWN") {
      router.push("/workspace/parsers/" + parserId +
        "/rules/" + rule.id +
        "?editorType=ruleProperties" +
        "&documentId=" + documentId +
        "&pageNum=" + pageNum)
    } else {
      router.push("/workspace/parsers/" + parserId +
        "/rules/" + rule.id +
        "?editorType=" + editorType +
        "&documentId=" + documentId +
        "&pageNum=" + pageNum)
    }
  }

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.container}>
        <div className={styles.editorWrapper}>
          <div xs="2" className={styles.sidebarWrapper} style={{width: openSidebar ? "279px": 0 }}>
            <div className={styles.parsingRulesHeader}>
              Data Parsing Rules
            </div>
            <div className={styles.parsingRules}>
              <ul>
                {rules && rules.map((rule, ruleIndex) => (
                  <li key={ruleIndex} onClick={(e) => liRuleClickHandler(e, rule)}>
                    <div className={styles.parsingRuleWrapper}>
                      <div className={styles.parsingRuleTxtWrapper}>
                        <div className={styles.parsingRuleName}>
                        {rule.id == ruleId && (
                          <strong>{rule.name}</strong>
                        )}
                        {rule.id != ruleId && (
                          <span>{rule.name}</span>
                        )}
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className={styles.parsingRulesFooter}>
              <Link href={"/workspace/parsers/" + parserId + "/rules"}>&#60; Exit Parsing Rules Editor</Link>
            </div>
          </div>
          <div className={styles.workbenchWrapper} style={{width: openSidebar ? "calc(100% - 280px)": "99%" }}>
            {children}
          </div>
        </div>
        <div className={styles.sidebarSizeControlDiv} style={{ left: openSidebar ? "225px": "10px" }}>
          {openSidebar && (
            <Button onClick={toggleSidebarHandler}><i className="bi bi-arrow-left"></i></Button>
          )}
          {!openSidebar && (
            <Button onClick={toggleSidebarHandler}><i className="bi bi-arrow-right"></i></Button>
          )}
        </div>
        <ToastContainer position="bottom-center" className="p-3">
          <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
            <Toast.Body>{toastMessage}</Toast.Body>
          </Toast>
        </ToastContainer>
      </div>
    </>
  )
}