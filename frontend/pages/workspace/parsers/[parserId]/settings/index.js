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

  const [updatedParser, setUpdatedParser] = useState(false)

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

  const parserNameChangeHandler = (e) => {
    let updatedParser = {...parser}
    updatedParser.name = e.target.value
    setParser(updatedParser)
  }

  const parserSaveBtnClickHandler = () => {
    updateParser()
    setUpdatedParser(!updatedParser)
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

  const openAIMetricsTenantIdChangeHandler = (e) => {
    console.log(e.target.value)
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsTenantId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey
    })
  }

  const openAIMetricsClientIdChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsClientId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey
    })
  }

  const openAIMetricsClientSecretChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsClientSecret = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey
    })
  }

  const openAIMetricsSubscriptionIdChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsSubscriptionId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey
    })
  }

  const openAIMetricsServiceNameChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsServiceName = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey
    })
  }

  const openAIMetricsSaveBtnClickHandler = () => {
    updateParser()
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
    <WorkspaceLayout key={updatedParser}>
      <div className={styles.settingsWrapper}>
        <h1>Settings</h1>
        {parser && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Parser Name</Card.Title>
              <Form.Group className="mb-3" controlId="formParserName">
                <Form.Control onChange={parserNameChangeHandler} value={parser.name}/>
              </Form.Group>
              <Button variant="primary" onClick={parserSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
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
        {console.log(parser)}
        {parser && parser.openAiMetricsKey && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Open AI Metrics</Card.Title>
              <Form.Group className="mb-3" controlId="formOpenAIMetricsKeyTenantId">
                <Form.Label>Open AI Metrics Tenant ID</Form.Label>
                <Form.Control onChange={openAIMetricsTenantIdChangeHandler} value={parser.openAiMetricsKey.openAiMetricsTenantId}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIMetricsKeyClientId">
                <Form.Label>Open AI Metrics Client ID</Form.Label>
                <Form.Control onChange={openAIMetricsClientIdChangeHandler} value={parser.openAiMetricsKey.openAiMetricsClientId}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIMetricsClientSecret">
                <Form.Label>Open AI Metrics Client Secret</Form.Label>
                <Form.Control onChange={openAIMetricsClientSecretChangeHandler} value={parser.openAiMetricsKey.openAiMetricsClientSecret}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIMetricsSubscriptionId">
                <Form.Label>Open AI Metrics Subscription ID</Form.Label>
                <Form.Control onChange={openAIMetricsSubscriptionIdChangeHandler} value={parser.openAiMetricsKey.openAiMetricsSubscriptionId}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIMetricsServiceName">
                <Form.Label>Open AI Metrics Service Name</Form.Label>
                <Form.Control onChange={openAIMetricsServiceNameChangeHandler} value={parser.openAiMetricsKey.openAiMetricsServiceName}/>
              </Form.Group>
              <Button variant="primary" onClick={openAIMetricsSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </WorkspaceLayout>
  )
}

export default Settings