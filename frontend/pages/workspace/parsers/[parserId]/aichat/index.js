
import { useState, useEffect, useRef, useCallback } from 'react'

import Head from "next/head"

import { useRouter } from 'next/router'

import { v4 as uuidv4 } from 'uuid'

import { produce } from 'immer';

import Image from "next/image";
import Link from "next/link";

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import { Nav } from "react-bootstrap";

import Select from 'react-select'

import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch"

import untruncateJson from "untruncate-json"

const FileDownload = require('js-file-download')

const ExcelJS = require('exceljs')

const FileSaver = require('file-saver')

import AIChatLayout from '../../../../../layouts/aichat'

import service from '../../../../../service'

import styles from '../../../../../styles/AIChat.module.css'

const shiftCharCode = Δ => c => String.fromCharCode(c.charCodeAt(0) + Δ);

const isMultipleArrays = (chat) => {
  
  for (const [key, value] of Object.entries(chat)) {
    console.log("value: ", value)
    if (!Array.isArray(value)) {
      return false
    }
  }

  return true
}

const arrayRange = (start, stop, step) =>
    Array.from(
    { length: (stop - start) / step + 1 },
    (value, index) => start + index * step
)

const recursiveChatInExcel = (metadataSheet, chat, level = 0, currentLineIndex = 0) => {
  if (typeof chat === 'string' || typeof chat === 'number') {
    let rowValues = []
    for (let i=1; i<level; i++) {
      rowValues.push("")
    }
    rowValues.push(chat)
    debugger
    metadataSheet.addRow(rowValues)
    rowValues = []
    currentLineIndex++
  } else if (isMultipleArrays(chat)) {
    let rowValues = []
    Object.keys(chat).map((header, headerIndex) => {
      for (let i=1; i<level; i++) {
        rowValues.push("")
      }
      rowValues.push(header)
    })

    debugger
    metadataSheet.addRow(rowValues)
    rowValues = []
    currentLineIndex++

    Object.values(chat).map((chatRow, chatRowIndex) => {
      for (let i=1; i<level; i++) {
        rowValues.push("")
      }
      for (let i=0; i<chatRow.length; i++) {
        rowValues.push(chatRow[i])
      }
      debugger
      metadataSheet.addRow(rowValues)
      rowValues = []
      currentLineIndex++
    })
  } else if (Array.isArray(chat)) {
    let rowValues = []
    Object.keys(chat[0]).map((header, headerIndex) => {
      for (let i=1; i<level; i++) {
        rowValues.push("")
      }
      rowValues.push(header)
    })

    debugger
    metadataSheet.addRow(rowValues)
    rowValues = []
    currentLineIndex++

    chat.map((tableRow, tableRowIndex) => {
      let tableRowObjectKeys = Object.keys(tableRow)
      if (tableRowObjectKeys.length > 0) {
        {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => (
          rowValues.push(tableRow[tableRowObjectKey])
        ))}
        debugger
        metadataSheet.addRow(rowValues)
        rowValues = []
        currentLineIndex++
      }
    })
  } else if (typeof chat === 'object') {
    debugger
    level = level + 1
    Object.keys(chat).map((objectKey, objectKeyIndex) => {
      let rowValues = []
      for (let i=1; i<level; i++) {
        rowValues.push("")
      }
      rowValues.push(objectKey)
      let row = metadataSheet.addRow(rowValues)
      row.font = {
        bold: true
      }
      rowValues = []
      currentLineIndex++
      currentLineIndex = recursiveChatInExcel(metadataSheet, chat[objectKey], level=level, currentLineIndex=currentLineIndex)
    })
  }

  if (level == 0) {
    return metadataSheet
  } else {
    debugger
    return currentLineIndex
  }
}

const RecursiveChat = ({chat}) => {
  console.log("raw: ", chat)
  if (typeof chat === 'string' || typeof chat === 'number') {
    console.log("string: ", chat)
    return (
      <div className={styles.talkValue}>{chat}</div>
    )
  } else if (isMultipleArrays(chat)) {
    console.log("multiple arrays: ", chat)
    return (
        <div className="talk-table-div">
          <table className="talk-table">
            <thead>
              <tr>
                {Object.keys(chat).map((header, headerIndex) => {
                  return (
                    <td key={headerIndex}>{header}</td>
                  )
                })}
              </tr>
            </thead>
            <tbody>
              {(function renderTableBody() {
                let cols = Object.keys(chat)
                if (chat[cols[0]] == undefined) {
                  return (
                    <></>
                  )
                }
                let rows = arrayRange(0, chat[cols[0]].length - 1, 1)
                return (
                  <>
                    {rows.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {cols.map((col, colIndex) => {
                          if (Array.isArray(chat[col][row])) {
                            return (
                              <td key={colIndex}>{chat[col][row]}</td>
                            )
                          }
                          else if (typeof chat[col][row] == 'object') {
                            return (
                              Object.keys(chat[col][row]).map((objectKey, objectKeyIndex) => {
                                <td key={colIndex}><strong>{objectKey}: </strong>{chat[col][row][objectKey]}</td>
                              })
                            )
                          }
                        })}
                      </tr>
                    ))}
                  </>
                )
              })()}
            </tbody>
          </table>
        </div>
      )
  } else if (Array.isArray(chat)) {
    console.log("array: ", chat)
    if (chat.length == 0) return (<></>)
    
    return (
      <div className="talk-table-div">
        <table className="talk-table">
          <thead>
            <tr>
              {Object.keys(chat[0]).map((tableKey, tableKeyIndex) => {
                return (
                  <th key={tableKeyIndex}>{tableKey}</th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {chat.map((tableRow, tableRowIndex) => {
              let tableRowObjectKeys = Object.keys(tableRow)
              if (tableRowObjectKeys.length > 0) {
                return (
                  <tr key={tableRowIndex}>
                    {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => {
                      if (typeof tableRow[tableRowObjectKey] == 'object') {

                      } else {
                        return (
                          <td key={tableRowObjectKeyIndex}>{tableRow[tableRowObjectKey]}</td>
                        )
                      }
                    })}
                  </tr>
                )
              } else {
                return (
                  <tr key={tableRowIndex}></tr>
                )
              }
            })}
          </tbody>
        </table>
      </div>
    )
  } else if (typeof chat === 'object') {
    return (
      Object.keys(chat).map((objectKey, objectKeyIndex) => {
        return (
          <div style={{paddingLeft: 10}} key={objectKeyIndex}>
            <div className={styles.talkKeyToValue}>{objectKey}</div>
            {<RecursiveChat chat={chat[objectKey]} />}
          </div>
        )
      })
    )
  }
}

const AIChat = () => {

  const router = useRouter()

  let { pathname, parserId, documentId, pageNum = 1 } = router.query;

  const [parser, setParser] = useState(null)

  const [document, setDocument] = useState(null)

  const [textlines, setTextlines] = useState([])

  const [currentChatUuid, setCurrentChatUuid] = useState("")

  const [chatHistories, setChatHistories] = useState([])

  const [chatText, setChatText] = useState("")

  const [chatIsLoading, setChatIsLoading] = useState(false)

  const [parserDocuments, setParserDocuments] = useState([])

  const [changeDocumentModal, setChangeDocumentModal] = useState({
    show: false
  })

  const [completedMark, setCompletedMark] = useState(false)

  const [imageUri, setImageUri] = useState(null)
  const [imageRef, setImageRef] = useState()

  const [showDocumentPagePreview, setShowDocumentPagePreview] = useState(true)

  const sidebarRef = useRef(null)
  const [isResizing, setIsResizing] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState("50%")

  const chatMessagesRef = useRef(null);

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const updateParser = () => {
    service.put("parsers/" + parserId + "/",
      parser,
      response => {
      }
    )
  }

  const getDocument = () => {
    if (!parserId) return
    if (!documentId) return
    service.get("documents/" + documentId + "/?parserId=" + parserId, response => {
      setDocument(response.data)
    })
  }

  const getDocumentPageImage = () => {
    if (!documentId) return
    if (!pageNum) return
    service.getFile("documents/" + documentId + "/pages/" + pageNum + "/image/",
      (response) => {
        let data = `data:${
          response.headers["content-type"]
        };base64,${new Buffer(response.data, "binary").toString("base64")}`
        setImageUri(data)
      })
  }

  const getTextlines = () => {
    if (!parserId) return
    if (!documentId) return
    if (!pageNum) return
    service.get("parsers/" + parserId + "/document/" + documentId + "/pages/" + pageNum + "/extract_all_text/", response => {
      setTextlines(response.data)
    })
  }

  const refreshChatHistories = () => {
    setChatHistories([])
    if (parser && parser.chatbot && parser.chatbot.openAiDefaultQuestion && parser.chatbot.openAiDefaultQuestion.trim().length > 0) {
      chatTextSendHandler(parser.chatbot.openAiDefaultQuestion)
    }
  }

  const prevPage = () => {
    if (pageNum <= 1) return
    let newPageNum = parseInt(pageNum) - 1
    router.push({
      pathname,
      query: {
        ...router.query,
        pageNum: newPageNum
      },
    })
  }

  const nextPage = () => {
    if (pageNum >= document.documentPages.length) return
    let newPageNum = parseInt(pageNum) + 1
    router.push({
      pathname,
      query: {
        ...router.query,
        pageNum: newPageNum
      },
    })
    //refreshChatHistories()
  }

  const toggleDocumentPagePreviewHandler = () => {
    setShowDocumentPagePreview(!showDocumentPagePreview)
  }

  const chatTextChangeHandler = (e) => {
    setChatText(e.target.value)
  }

  const chatTextKeyDownHandler = (e) => {
    if ((e.keyCode == 10 || e.keyCode == 13) && e.ctrlKey) {
      chatTextSendHandler(e.target.value)
      setChatText("")
    }
  }

  const chatTextSendHandler = async (chatText) => {
    setChatIsLoading(true)
    setChatText("")

    let updatedChatHistories = [...chatHistories]

    updatedChatHistories.push({
        uuid: uuidv4(),
        from: "staff",
        chat: chatText
      })
    updatedChatHistories.push({
        uuid: uuidv4(),
        from: "machine",
        chat: { "Message": "Loading..." },
        export_xlsx: true
      })

    setChatHistories(updatedChatHistories)
        
    let chatData = ""

    try {
      await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + "parsers/" + parserId + "/documents/" + documentId + "/pages/" + pageNum + "/ask_chatbot/", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: chatText
        })
      }).then(async (response) => {

        if (!response.ok) {
          console.error(response)
          throw new Error(`${response.status} ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          try {
            const { value, done } = await reader.read();
            if (done) {
              setChatIsLoading(false);
              break;
            }

            const decodedChunk = decoder.decode(value, { stream: true })

            chatData = `${chatData}${decodedChunk}`

            updatedChatHistories = updatedChatHistories.map((chatHisory, chatHisoryIndex) => {   
              if(chatHisoryIndex == (updatedChatHistories.length - 1)){
                  const updatedChatHistory = {...chatHisory}
                  try {
                    updatedChatHistory.chat = JSON.parse(untruncateJson(chatData))
                  } catch(error) {
                    console.error(error)
                    updatedChatHistory.chat = { "message": chatData}
                  }
                  return updatedChatHistory;
              }
              return chatHisory
            })

            setChatHistories(updatedChatHistories)
            console.log("updatedChatHistories: ", updatedChatHistories)

          } catch(error) {

            console.error(error)
            console.log(chatHistories)
            setChatIsLoading(false);

          }
        }
      })
    } catch(error) {
      console.error(error)
      updatedChatHistories = updatedChatHistories.map((chatHisory, chatHisoryIndex) => {   
        if(chatHisoryIndex == (updatedChatHistories.length - 1)){
            const updatedChatHistory = {...chatHisory}
            updatedChatHistory.chat = {
              "Error": "Seems we are encountering network errors. Please try again. If problem persists, please contact system administrator."
            }
            return updatedChatHistory;
        }
        return chatHisory
      })

      setChatHistories(updatedChatHistories)
      setChatIsLoading(false);
    }
    
  }

  const downloadExcelBtnClickHandler = async () => {
    if (chatHistories.filter(ch => ch.from == "machine").length == 0) return

    const workbook = new ExcelJS.Workbook()

    let latestMachineResponses = chatHistories.filter(ch => ch.from == "machine" && ch.export_xlsx)
    
    let metadataSheet = workbook.addWorksheet("Metadata")
    debugger
    metadataSheet = recursiveChatInExcel(metadataSheet, latestMachineResponses[latestMachineResponses.length - 1].chat)

    /*for (let i=0; i<latestMachineResponses.length; i++) {
      let chatCounter = i + 1
      let rowIndex = 0
      let latestMachineResponse = latestMachineResponses[i].chat
      let metadataWorksheet = workbook.addWorksheet(chatCounter + ".Metadata")
      Object.entries(latestMachineResponse)
        .map(([key, value]) => {
          if (!Array.isArray(value)) {
            let rowValues = []
            rowValues[1] = key
            rowValues[2] = value

            if (typeof value === 'object' && Object.entries(value).length == 1 && Array.isArray(value[0])) {
              Object.entries(latestMachineResponse)
                .map(([key, value]) => {
                let itemTableName = key
                let itemTableRows = value
                if (itemTableRows.length > 0) {
                  let itemTableSheet = workbook.addWorksheet(chatCounter + ". " + itemTableName)
                  let rowValues = []
                  let itemTableColIndex = 1
                  Object.entries(itemTableRows[0])
                  .map(([tableKey, tableValue]) => {
                    rowValues[itemTableColIndex] = tableKey
                    itemTableColIndex++
                  })
                  itemTableSheet.addRow(rowValues)
                  
                  
                  for (let j=0; j<itemTableRows.length; j++) {
                    let itemTableRow = itemTableRows[j]
                    rowValues = []

                    itemTableColIndex = 1
                    Object.entries(itemTableRow)
                    .map(([tableKey, tableValue]) => {
                      rowValues[itemTableColIndex] = tableValue
                      itemTableColIndex++
                    })
                    itemTableSheet.addRow(rowValues)
                  }
                }
              })
            }

            metadataWorksheet.addRow(rowValues)
          } else {
            let itemTableName = key
            let itemTableRows = value
            if (itemTableRows.length > 0) {
              let itemTableSheet = workbook.addWorksheet(chatCounter + ". " + itemTableName)
              let rowValues = []
              let itemTableColIndex = 1
              Object.entries(itemTableRows[0])
              .map(([tableKey, tableValue]) => {
                rowValues[itemTableColIndex] = tableKey
                itemTableColIndex++
              })
              itemTableSheet.addRow(rowValues)
              
              
              for (let j=0; j<itemTableRows.length; j++) {
                let itemTableRow = itemTableRows[j]
                rowValues = []

                itemTableColIndex = 1
                Object.entries(itemTableRow)
                .map(([tableKey, tableValue]) => {
                  rowValues[itemTableColIndex] = tableValue
                  itemTableColIndex++
                })
                itemTableSheet.addRow(rowValues)
              }
            }
          }
      })
    }*/
    
    const buffer = await workbook.xlsx.writeBuffer()
    FileSaver.saveAs(new Blob([buffer]), "Cashew AI Chatbot Result.xlsx")
  }

  const markAsCompletedBtnClickHandler = (e) => {
    console.log(e)
    service.post("documents/" + documentId + "/pages/" + pageNum + "/mark_as_chatbot_completed/", 
    {
      status: true
    }, 
    response => {
      getDocument()
    }, errorResponse => {
      console.error(errorResponse)
    })
  }

  const markAsIncompletedBtnClickHandler = (e) => {
    service.post("documents/" + documentId + "/pages/" + pageNum + "/mark_as_chatbot_completed/", 
    {
      status: false
    }, 
    response => {
      getDocument()
    }, errorResponse => {
      console.error(errorResponse)
    })
  }

  const downloadPDFBtnClickHandler = (e) => {
    service.getFileBlob("documents/" + documentId + "/searchable-pdf/", (response) => {
      FileDownload(response.data, document.guid + "-searchable.pdf")
    })
  }

  const downloadTextBtnClickHandler = () => {
    console.log(textlines)
    service.get("parsers/" + parserId + "/document/" + documentId + "/extract_all_text/", response => {
      let filename = document.guid + "-text.txt"
      let element = window.document.createElement('a')
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(response.data.join("\n")))
      element.setAttribute('download', filename)

      element.style.display = 'none'
      window.document.body.appendChild(element)

      element.click()

      window.document.body.removeChild(element)
    })
    
  }

  const timeout = async (delay) => {
    return new Promise( res => setTimeout(res, delay) );
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
    setChatHistories([])
    router.push({
      pathname,
      query: {
        ...router.query,
        documentId: e.target.value,
        pageNum: 1
      },
    })
  }

  const startResizing = useCallback((mouseDownEvent) => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (mouseMoveEvent) => {
      if (isResizing) {
        console.log(mouseMoveEvent)
        setSidebarWidth(
          mouseMoveEvent.clientX -
            sidebarRef.current.getBoundingClientRect().left
        );
      }
    },
    [isResizing]
  );

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  useEffect(() => {
    if (!router.isReady) return
    if (!parserId) return
    getParserDocuments()
  }, [router.isReady, parserId])

  useEffect(() => {
    if (!router.isReady) return
    getDocument()
  }, [router.isReady, parserId, documentId])

  useEffect(() => {
    if (!router.isReady) return
    getDocumentPageImage()
    getTextlines()
  }, [router.isReady, parserId, documentId, pageNum])

  useEffect(() => {
    if (!router.isReady) return
    refreshChatHistories()
  }, [router.isReady, documentId])

  useEffect(() => {
    if (!router.isReady) return
    chatMessagesRef.current?.scrollIntoView({behavior: 'smooth'})
  }, [router.isReady, chatHistories])

  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [resize, stopResizing]);

  const renderChat = (chat) => {
    if (typeof chat === 'string' || typeof chat === Number) {
      console.log(chat)
      return (
        <div className={styles.talkKeyToValue}>{chat}</div>
      )
    } else if (Array.isArray(chat)) {
      return (
        <div className="talk-table-div" key={keyIndex}>
          <p>{key}: </p>
          <table className="talk-table">
            <thead>
              <tr>
                {Object.keys(tableJSON[0]).map((tableKey, tableKeyIndex) => {
                  return (
                    <th key={tableKeyIndex}>{tableKey}</th>
                  )
                })}
              </tr>
            </thead>
            <tbody>
              {tableJSON.map((tableRow, tableRowIndex) => {
                let tableRowObjectKeys = Object.keys(tableRow)
                if (tableRowObjectKeys.length > 0) {
                  return (
                    <tr key={tableRowIndex}>
                      {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => (
                        <td key={tableRowObjectKeyIndex}>{tableRow[tableRowObjectKey]}</td>
                      ))}
                    </tr>
                  )
                } else {
                  return (
                    <tr key={tableRowIndex}></tr>
                  )
                }
              })}
            </tbody>
          </table>
        </div>
      )
    } else if (typeof chat === 'object') {
      Object.keys(chat).map((objectKey, objectKeyIndex) => {
      return (
        <>
          <div className={styles.talkKeyToValue}>{objectKey}</div>
          {renderChat(chat[objectKey])}
        </>
      )
      })
    }
  }

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
                style={{ paddingLeft: 0, paddingRight: 0, textAlign: "center", lineHeight: "52px" }}
              >
                {console.log(parserDocuments)}
                {console.log(documentId)}
                {parserDocuments && parserDocuments.length > 0 && documentId && (
                  <>
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
          <hr className={styles.headerHr} />
          <main className={styles.main + " d-flex flex-column"}>
            <div
              className="row d-flex flex-grow-1"
              style={{ padding: 0, margin: 0, flexDirection: "row", height: "60%" }}
            >
              <div
                className="col-12 col-md-6 d-flex"
                style={{ position: "relative", paddingLeft: 0, paddingRight: 0, width: sidebarWidth, overflow: "hidden", borderRight: "3px solid #000", height: "100%" }}
                ref={sidebarRef}
              >
                {document && document.documentPages.filter(dp => dp.pageNum == pageNum && dp.ocred).length > 0 && (
                  <TransformWrapper 
                    className="my-react-transform-component"
                    initialScale={0.3}
                    minScale={0.2} maxScale={1}
                    centerZoomedOut={false} customTransform={(x, y, scale) => {
                      const a = scale;
                      const b = 0;
                      const c = 0;
                      const d = scale;
                      const tx = x;
                      const ty = y;
                      return `matrix3d(${a}, ${b}, 0, 0, ${c}, ${d}, 0, 0, 0, 0, 1, 0, ${tx}, ${ty}, 0, 1)`;
                    }}> 
                    {({ zoomIn, zoomOut, resetTransform, ...rest }) => (
                      <>
                        <div className={styles.tools} style={{ display: showDocumentPagePreview ? "block": "none" }}>
                          <Button className={styles.toolsBtn} onClick={() => zoomIn()}>Zoom in</Button>
                          <Button className={styles.toolsBtn} onClick={() => zoomOut()}>Zoom out</Button>
                          <Button className={styles.toolsBtn} onClick={() => resetTransform()}>Reset</Button>
                          <Button className={styles.toolsBtn} onClick={() => prevPage()}><i className="bi bi-arrow-left"></i></Button>
                          <Button className={styles.toolsBtn}>Page {pageNum} of {document && document.documentPages.length}</Button>
                          <Button className={styles.toolsBtn} onClick={() => nextPage()}><i className="bi bi-arrow-right"></i></Button>
                          <Button className={styles.toolsBtn} onClick={() => downloadPDFBtnClickHandler()}><i className="bi bi-file-earmark-pdf"></i> Download</Button>
                        </div>
                        <TransformComponent>
                          <div style={{marginTop: 150}}>
                            <img className={styles.documentPageImg} src={imageUri} ref={imageRef}/>
                          </div>
                        </TransformComponent>
                      </>
                    )}
                  </TransformWrapper>
                )}
                {document && document.documentPages.filter(dp => dp.pageNum == pageNum && dp.ocred).length <= 0 && (
                  <TransformWrapper 
                    className="my-react-transform-component"
                    wheel={{disabled: true}}
                    minScale={0.2} maxScale={1} maxPositionY={0}
                    centerZoomedOut={false}> 
                    {({ zoomIn, zoomOut, resetTransform, ...rest }) => (
                      <>
                        <div className={styles.tools} style={{ display: showDocumentPagePreview ? "block": "none" }}>
                          <Button className={styles.toolsBtn} onClick={() => zoomIn()}>Zoom in</Button>
                          <Button className={styles.toolsBtn} onClick={() => zoomOut()}>Zoom out</Button>
                          <Button className={styles.toolsBtn} onClick={() => resetTransform()}>Reset</Button>
                          <Button className={styles.toolsBtn} onClick={() => prevPage()}><i className="bi bi-arrow-left"></i></Button>
                          <Button className={styles.toolsBtn}>Page {pageNum} of {document && document.documentPages.length}</Button>
                          <Button className={styles.toolsBtn} onClick={() => nextPage()}><i className="bi bi-arrow-right"></i></Button>
                          <Button className={styles.toolsBtn} onClick={() => downloadPDFBtnClickHandler()}><i className="bi bi-file-earmark-pdf"></i> Download</Button>
                        </div>
                        <TransformComponent>

                        </TransformComponent>
                        <div style={{ width: 100, height: 100, margin: "auto" }}>This page is undergoing OCR. Please wait...</div>
                      </>
                    )}
                  </TransformWrapper>
                )}
              </div>
              <div className={styles.sidebarResizer} onMouseDown={startResizing}></div>
              {document && document.documentPages.filter(dp => dp.pageNum == pageNum && dp.ocred).length > 0 && (
              <div className={styles.pageText}>
                <div className={styles.tools} style={{ display: showDocumentPagePreview ? "block": "none" }}>
                  <Button className={styles.toolsBtn} onClick={() => downloadTextBtnClickHandler()}><i className="bi bi-card-text"></i> Download</Button>
                </div>
                <div className={styles.streamTableDiv}>
                  <table className={styles.streamTable}>
                    <tbody>
                      {textlines.map((row, rowIndex) => {
                        return (
                          <tr key={rowIndex}>
                            {/* .replace(" ", "　").replace(/[!-~]/g, shiftCharCode(0xFEE0)) */}
                            <td>{row.replace(/ /g, '\u00a0')}</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
              )}
            </div>
            <div className="d-flex flex-grow-1"
                style={{ padding: 0, margin: 0, flexDirection: "column", overflowY: "hidden", borderTop: "2px solid #000" }}>
              <div className={styles.chatMessages}>
                <div className={[styles.talkBubble, styles.triRight, styles.round, styles.btmLeft].join(" ")}>
                  <div className={styles.talktext}>
                    <p>Ask me anything about this document.</p>
                  </div>
                </div>
                {chatHistories && chatHistories.map((chatHistory, chatHistoryIndex) => 
                  <div key={chatHistory.uuid}>
                    {chatHistory.from == "staff" && (
                      <div className={[styles.talkBubble, styles.triRight, styles.border, styles.btmRightIn, "right"].join(" ")}>
                        <div className={styles.talktext}>
                          <p>{chatHistory.chat}</p>
                        </div>
                      </div>
                    )}
                    {chatHistory.from == "machine" && (
                      <div className={[styles.talkBubble, styles.triRight, styles.round, styles.btmLeft].join(" ")}>
                        <div className={styles.talkActionDiv}>
                          <Form.Check
                            type="checkbox"
                            checked={chatHistory.export_xlsx}
                            onChange={() => {
                              setChatHistories(chatHistories.map((ch, chIndex) => {
                                if (chIndex == chatHistoryIndex) {
                                  return {...ch, export_xlsx: !ch.export_xlsx}
                                } else {
                                  return {...ch}
                                }
                              }))
                            }}
                          />
                        </div>
                        <div className={styles.talktext}>
                          {/*Array.isArray(chatHistory.chat) && chatHistory.chat.length > 0 && (
                            <div className="talk-table-div" key={key}>
                              <table className="talk-table">
                                <thead>
                                  <tr>
                                    {Object.keys(chatHistory.chat[0]).map((tableKey, tableKeyIndex) => {
                                      console.log(tableKey)
                                      return (
                                        <th key={tableKeyIndex}>{tableKey}</th>
                                      )
                                    })}
                                  </tr>
                                </thead>
                                <tbody>
                                  {chatHistory.chat.map((tableRow, tableRowIndex) => {
                                    let tableRowObjectKeys = Object.keys(tableRow)
                                    if (tableRowObjectKeys.length > 0) {
                                      return (
                                        <tr key={tableRowIndex}>
                                          {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => (
                                            <td key={tableRowObjectKeyIndex}>{tableRow[tableRowObjectKey]}</td>
                                          ))}
                                        </tr>
                                      )
                                    } else {
                                      return (
                                        <tr key={tableRowIndex}></tr>
                                      )
                                    }
                                  })}
                                </tbody>
                              </table>
                            </div>
                                )*/}
                          {<RecursiveChat chat={chatHistory.chat}/>}
                          {/*!Array.isArray(chatHistory.chat) && Object.keys(chatHistory.chat).length > 0 && Object.keys(chatHistory.chat).map((key, keyIndex) => {
                            if (typeof chatHistory.chat === 'string') {
                              <div className={styles.talkKeyToValue}>{chatHistory.chat[key]}</div>
                            } else if (typeof chatHistory.chat[key] === 'string') {
                              return (
                                <div className={styles.talkKeyToValue} key={keyIndex}>{key}: {chatHistory.chat[key]}</div>
                              )
                            } else if (Array.isArray(chatHistory.chat[key])) {
                              if (Array.isArray(chatHistory.chat[key]) && chatHistory.chat[key].length > 0) {
                                let tableJSON = chatHistory.chat[key]
                                if (typeof tableJSON[0] === 'string') {
                                  return (
                                    <div key={keyIndex}>
                                      {tableJSON.map((data, dataIndex) => (
                                        <div className={styles.talkKeyToValue} key={dataIndex}>{key}: {data}</div>
                                      ))}
                                    </div>
                                  )
                                } else {
                                  return (
                                    <div className="talk-table-div" key={keyIndex}>
                                      <p>{key}: </p>
                                      <table className="talk-table">
                                        <thead>
                                          <tr>
                                            {Object.keys(tableJSON[0]).map((tableKey, tableKeyIndex) => {
                                              return (
                                                <th key={tableKeyIndex}>{tableKey}</th>
                                              )
                                            })}
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {tableJSON.map((tableRow, tableRowIndex) => {
                                            let tableRowObjectKeys = Object.keys(tableRow)
                                            if (tableRowObjectKeys.length > 0) {
                                              return (
                                                <tr key={tableRowIndex}>
                                                  {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => (
                                                    <td key={tableRowObjectKeyIndex}>{tableRow[tableRowObjectKey]}</td>
                                                  ))}
                                                </tr>
                                              )
                                            } else {
                                              return (
                                                <tr key={tableRowIndex}></tr>
                                              )
                                            }
                                          })}
                                        </tbody>
                                      </table>
                                    </div>
                                  )
                                }
                              }
                            } else if (!Array.isArray(chatHistory.chat[key]) && typeof chatHistory.chat[key] === 'object') {
                              let objectJSON = chatHistory.chat[key]
                              let objectsHtml = (<></>)
                              if (Object.keys(objectJSON).length > 0) {
                                objectsHtml = Object.keys(objectJSON).map((objectKey, objectKeyIndex) => {
                                  //console.log(objectKey, ": ", objectJSON[objectKey])
                                  if (typeof objectJSON[objectKey] === 'string') {
                                    return (
                                      <div key={objectKeyIndex} className={styles.talkKeyToValue}>{objectKey}: {objectJSON[objectKey]}</div>
                                    )
                                  } else if (Array.isArray(objectJSON[objectKey])){
                                    let tableJSON = objectJSON[objectKey]
                                    console.log("Anchor: ", tableJSON)
                                    if (tableJSON.length > 0) {
                                      if (typeof tableJSON[0] === 'string') {
                                        return (
                                          <div className="talk-table-div">
                                            <table className="talk-table">
                                              <tbody>
                                                {tableJSON.map(row => {
                                                  return (
                                                    <tr>{row}</tr>
                                                  )
                                                })}
                                              </tbody>
                                            </table>
                                          </div>
                                        )
                                      } else {

                                        return (
                                          <div className="talk-table-div" key={key}>
                                            <p>{key}: </p>
                                            <table className="talk-table">
                                              <thead>
                                                <tr>
                                                  {Object.keys(tableJSON[0]).map((tableKey, tableKeyIndex) => {
                                                    return (
                                                      <th key={tableKeyIndex}>{tableKey}</th>
                                                    )
                                                  })}
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {tableJSON.map((tableRow, tableRowIndex) => {
                                                  let tableRowObjectKeys = Object.keys(tableRow)
                                                  if (tableRowObjectKeys.length > 0) {
                                                    return (
                                                      <tr key={tableRowIndex}>
                                                        {tableRowObjectKeys.map((tableRowObjectKey, tableRowObjectKeyIndex) => (
                                                          <td key={tableRowObjectKeyIndex}>{tableRow[tableRowObjectKey]}</td>
                                                        ))}
                                                      </tr>
                                                    )
                                                  } else {
                                                    return (
                                                      <tr key={tableRowIndex}></tr>
                                                    )
                                                  }
                                                })}
                                              </tbody>
                                            </table>
                                          </div>
                                        )
                                        
                                      }
                                    }
                                  }
                                  
                                })
                              }
                              return objectsHtml
                            } 
                          })*/}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <div className={styles.actions}>
                  <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={downloadExcelBtnClickHandler} ref={chatMessagesRef}>Download as Excel</Button>
                  {document && document.documentPages.find(dp => dp.pageNum == pageNum).chatbotCompleted && (
                    <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={markAsIncompletedBtnClickHandler}>Mark as incompleted</Button>
                  )}
                  {document && !document.documentPages.find(dp => dp.pageNum == pageNum).chatbotCompleted && (
                    <Button style={{marginLeft: 10, marginBottom: 10, marginTop: 10, whiteSpace: "nowrap"}} onClick={markAsCompletedBtnClickHandler}>Mark as completed</Button>
                  )}
                </div>
              </div>
              <div className={styles.chatTextfield}>
                <Form.Control
                  type="text"
                  id="chatTextfield"
                  style={{ "borderRadius": 0, "resize": "none" }}
                  placeholder={chatIsLoading ? "Please wait..." : "Ask me anything..."}
                  as="textarea"
                  row="2"
                  value={chatText}
                  disabled={chatIsLoading}
                  onChange={chatTextChangeHandler}
                  onKeyDown={chatTextKeyDownHandler}
                />
                <Button style={{ borderRadius: 0}} onClick={() => chatTextSendHandler(chatText)}>Send</Button>
              </div>
            </div>
            {/*<Button style={{position: "absolute", bottom: 71, left: 5, display: showDocumentPagePreview ? "none" : "block"}} onClick={() => toggleDocumentPagePreviewHandler()}>Show</Button>
            <Button style={{position: "absolute", bottom: 71, left: 5, display: showDocumentPagePreview ? "block" : "none"}} onClick={() => toggleDocumentPagePreviewHandler()}>Hide</Button>*/}
          </main>
        </>
        <footer className={styles.footer}>
          <div style={{ width: "100%", padding: "0 10px" }}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm" style={{ padding: "5px" }}>
                <div className={styles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}

export default AIChat