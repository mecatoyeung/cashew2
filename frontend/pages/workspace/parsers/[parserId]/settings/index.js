import { useState, useEffect } from 'react'

import { useRouter } from 'next/router'

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'

import Select from 'react-select'

import WorkspaceLayout from '../../../../../layouts/workspace'

import service from '../../../../../service'

import styles from '../../../../../styles/Settings.module.css'

const ocrOptions = [
  {
    label: "No OCR",
    value: "NO_OCR"
  },
  {
    label: "Google Vision OCR (Cloud, Paid, very good at English/Traditional Chinese/Simplified Chinese)",
    value: "GOOGLE_VISION"
  },
  {
    label: "DocTR (On Premise, Free, very good at English and cannot recognize Traditional Chinese and Simplified Chinese)",
    value: "DOCTR"
  },
  {
    label: "PaddleOCR (On Premise, Free, very good at Simplified Chinese, good at English/Japanese/Korean and fair at Traditional Chinese)",
    value: "PADDLE_OCR"
  },
  {
    label: "Omnipage OCR (On Premise, Paid, very good at Traditional (Especially 香港常用字)/Simplified Chinese/English.)",
    value: "OMNIPAGE_OCR"
  }
]

const paddleOCRLangOptions = [
  {
    label: "Simplified Chinese",
    value: "ch"
  },
  {
    label: "English",
    value: "en"
  },
  {
    label: "Traditional Chinese",
    value: "ch_tra"
  },
  {
    label: "Japanese",
    value: "japan"
  },
  {
    label: "Korean",
    value: "korean"
  },
  {
    label: "French",
    value: "fr"
  },
  {
    label: "German",
    value: "german"
  },
  {
    label: "Vietnamese",
    value: "vi"
  }
]

const omnipageOCRLangOptions = [
  {
    label: "Traditional Chinese",
    value: "LANG_CHT"
  },
  {
    label: "Simplified Chinese",
    value: "LANG_CHS"
  },
  {
    label: "English",
    value: "LANG_ENG"
  }
]

const chatBotOptions = [
  {
    label: "No Chatbot",
    value: "NO_CHATBOT"
  },
  {
    label: "Open AI",
    value: "OPEN_AI"
  },
  {
    label: "On Premise AI",
    value: "ON_PREMISE_AI"
  }
]

const Settings = () => {

  const router = useRouter()

  const [parser, setParser] = useState(null)

  const [importModal , setImportModal] = useState({
    show: false,
    selectedFile: null,
    parserName: "",
    parserNameMatched: true
  })

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const importBtnClickHandler = () => {

  }

  const closeImportModalHandler = () => {

  }

  const importFileChangeHandler = () => {

  }

  const exportBtnClickHandler = () => {
    service.get("parsers/" + parserId + "/export/", response => {

      const jsonString = `data:text/json;chatset=utf-8,${encodeURIComponent(
        JSON.stringify(response.data)
      )}`

      const link = document.createElement("a")
      link.href = jsonString
      link.download = "parser-" + parserId + ".json"

      link.click();
    })
  }

  const parserNameChangeHandler = () => {
    
  }

  const confirmImportParserBtnClickHandler = () => {

  }

  const ocrTypeChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.ocrType = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const googleVisionOcrApiKeyChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.googleVisionOcrApiKey = e.target.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const paddleOCRLanguageChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.paddleOCRLanguage = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const ocrSaveBtnClickHandler = () => {
    updateParser()
  }

  const chatbotTypeChangeHandler = (e) => {
    let updatedChatBot = { ...parser.chatbot }
    updatedChatBot.chatbotType = e.value
    setParser({
      ...parser,
      chatbot: updatedChatBot
    })
  }

  const chatbotOpenAIResourceNameChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiResourceName = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotOpenAIApiKeyChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiApiKey = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotOpenAIDeploymentChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiDeployment = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotOpenAIDefaultQuestionChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiDefaultQuestion = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotBaseUrlChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.baseUrl = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const openAIEnabledChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.enabled = e.target.checked
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const openAIResourceNameChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiResourceName = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const openAIApiKeyChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiApiKey = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const openAIDeploymentChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiDeployment = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const chatBotSaveBtnClickHandler = () => {
    updateParser()
  }

  const openAISaveBtnClickHandler = () => {
    updateParser()
  }

  const updateParser = () => {
    service.put("parsers/" + parserId + "/",
      parser,
      response => {
      }
    )
  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  const { parserId } = router.query

  return (
    <WorkspaceLayout>
      <div className={styles.settingsWrapper}>
        <h1>Settings</h1>
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body>
            <Card.Title>Export</Card.Title>
            <Card.Text>
              Export and Import this parser to transfer between servers
            </Card.Text>
            <Button variant="primary" style={{ marginRight: 10 }} onClick={exportBtnClickHandler}>Export</Button>
          </Card.Body>
        </Card>
        {parser && parser.chatbot != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Chat Bot</Card.Title>
              <Form.Group className="mb-3" controlId="formChatBotType">
                <Select
                  options={chatBotOptions}
                  value={chatBotOptions.find(oo => oo.value == parser.chatbot.chatbotType)}
                  onChange={(e) => chatbotTypeChangeHandler(e)}
                  menuPlacement="auto"
                  menuPosition="fixed" />
              </Form.Group>
              {parser.chatbot.chatbotType == "OPEN_AI" && (
                <>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIResourceName">
                    <Form.Label>Open AI Resource Name</Form.Label>
                    <Form.Control onChange={chatbotOpenAIResourceNameChangeHandler} value={parser.chatbot.openAiResourceName}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIApiKey">
                    <Form.Label>Open AI API KEY</Form.Label>
                    <Form.Control onChange={chatbotOpenAIApiKeyChangeHandler} value={parser.chatbot.openAiApiKey}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIDeployment">
                    <Form.Label>Open AI Deplyment</Form.Label>
                    <Form.Control onChange={chatbotOpenAIDeploymentChangeHandler} value={parser.chatbot.openAiDeployment}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIDefaultQuestion">
                    <Form.Label>Open AI Default Question</Form.Label>
                    <Form.Control onChange={chatbotOpenAIDefaultQuestionChangeHandler} value={parser.chatbot.openAiDefaultQuestion}/>
                  </Form.Group>
                </>
              )}
              {parser.chatbot.chatbotType == "ON_PREMISE_AI" && (
                <>
                  <Form.Group className="mb-3" controlId="formChatbotBaseUrl">
                    <Form.Label>Base Url</Form.Label>
                    <Form.Control onChange={chatbotBaseUrlChangeHandler} value={parser.chatbot.baseUrl}/>
                  </Form.Group>
                </>
              )}
              <Button variant="primary" onClick={chatBotSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
        {parser && parser.openAi != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Open AI</Card.Title>
              <Form.Group className="mb-3" controlId="formOpenAIEnabled">
                <Form.Check // prettier-ignore
                  type="checkbox"
                  id={`default-formOpenAIEnabled`}
                  label={`Enabled`}
                  checked={parser.openAi.enabled}
                  onChange={openAIEnabledChangeHandler}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIResourceName">
                <Form.Label>Open AI Resource Name</Form.Label>
                <Form.Control onChange={openAIResourceNameChangeHandler} value={parser.openAi.openAiResourceName}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIApiKey">
                <Form.Label>Open AI API KEY</Form.Label>
                <Form.Control onChange={openAIApiKeyChangeHandler} value={parser.openAi.openAiApiKey}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIDeployment">
                <Form.Label>Open AI Deployment</Form.Label>
                <Form.Control onChange={openAIDeploymentChangeHandler} value={parser.openAi.openAiDeployment}/>
              </Form.Group>
              <Button variant="primary" onClick={openAISaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </WorkspaceLayout>
  )
}

export default Settings