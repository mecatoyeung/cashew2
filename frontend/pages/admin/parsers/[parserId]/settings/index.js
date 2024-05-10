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

import RangeSlider from 'react-bootstrap-range-slider'

import Select from 'react-select'

import AdminLayout from '../../../../../layouts/admin'

import service from '../../../../../service'

import 'react-bootstrap-range-slider/dist/react-bootstrap-range-slider.css'

import styles from '../../../../../styles/Settings.module.css'

const chatBotOptions = [
  {
    label: 'No Chatbot',
    value: 'NO_CHATBOT',
  },
  {
    label: 'Open AI',
    value: 'OPEN_AI',
  },
  {
    label: 'On Premise AI',
    value: 'ON_PREMISE_AI',
  },
]

const Settings = () => {
  const router = useRouter()

  const [parser, setParser] = useState(null)

  const [updatedParser, setUpdatedParser] = useState(false)

  const [parserErrorMessage, setParserErrorMessage] = useState('')
  const [permissionSettingsErrorMessage, setPermissionSettingsErrorMessage] =
    useState('')

  const [account, setAccount] = useState(null)
  const [users, setUsers] = useState([])
  const [groups, setGroups] = useState([])

  const [transferOwnerModal, setTransferOwnerModal] = useState({
    show: false,
    ownerId: null,
  })

  const getParser = () => {
    service.get('parsers/' + parserId + '/', (response) => {
      setParser(response.data)
    })
  }

  const getAccount = () => {
    service.get('account/', (response) => {
      setAccount(response.data)
    })
  }

  const getUsers = () => {
    if (!account) return
    service.get('users/', (response) => {
      setUsers(
        response.data.map((u) => {
          if (u.id == account.id) {
            return {
              value: u.id,
              label: u.profile.fullName + ' (current user)',
            }
          } else {
            return {
              value: u.id,
              label: u.profile.fullName,
            }
          }
        })
      )
    })
  }

  const getGroups = () => {
    service.get('groups/', (response) => {
      setGroups(
        response.data.map((u) => {
          return {
            value: u.id,
            label: u.name,
          }
        })
      )
    })
  }

  const parserNameChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.name = e.target.value
    setParser(updatedParser)
  }

  const pdfToImageDpiChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.pdfToImageDpi = e.target.value
    setParser(updatedParser)
  }

  const assumedTextWidthChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.assumedTextWidth = e.target.value
    setParser(updatedParser)
  }

  const assumedTextHeightChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.assumedTextHeight = e.target.value
    setParser(updatedParser)
  }

  const sameLineAcceptanceRangeChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.sameLineAcceptanceRange = e.target.value
    setParser(updatedParser)
  }

  const sameColumnAcceptanceRangeChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.sameColumnAcceptanceRange = e.target.value
    setParser(updatedParser)
  }

  const ownerChangeHandler = (e) => {
    let updatedParser = { ...parser }
    updatedParser.owner = e.value
    setParser(updatedParser)
  }

  const permittedUsersChangeHandler = (e) => {
    let updatedParser = { ...parser }
    let permittedUsers = []
    for (let i = 0; i < e.length; i++) {
      if (users.filter((u) => u.value == e[i].value).length > 0) {
        permittedUsers.push(e[i].value)
      }
    }
    updatedParser.permittedUsers = permittedUsers
    setParser(updatedParser)
  }

  const permittedGroupsChangeHandler = (e) => {
    let updatedParser = { ...parser }
    let permittedGroups = []
    for (let i = 0; i < e.length; i++) {
      if (groups.filter((u) => u.value == e[i].value).length > 0) {
        permittedGroups.push(e[i].value)
      }
    }
    updatedParser.permittedGroups = permittedGroups
    setParser(updatedParser)
  }

  const openTransferOwnerModalHandler = (e) => {
    let updatedTransferOwnerModal = { ...transferOwnerModal }
    updatedTransferOwnerModal.show = true
    updatedTransferOwnerModal.ownerId = parser.owner.id
    setTransferOwnerModal(updatedTransferOwnerModal)
  }

  const closeTransferOwnerModalHandler = (e) => {
    let updatedTransferOwnerModal = { ...transferOwnerModal }
    updatedTransferOwnerModal.show = false
    setTransferOwnerModal(updatedTransferOwnerModal)
  }

  const confirmTransferOwnerBtnClickHandler = () => {
    service.post(
      `parsers/${parserId}/transfer_owner/${transferOwnerModal.ownerId}/`,
      {},
      (response) => {
        let updatedTransferOwnerModal = { ...transferOwnerModal }
        updatedTransferOwnerModal.show = false
        setTransferOwnerModal(updatedTransferOwnerModal)
        getParser()
      }
    )
  }

  const transferOwnerChangeHandler = (e) => {
    let updatedTransferOwnerModal = { ...transferOwnerModal }
    updatedTransferOwnerModal.ownerId = e.value
    setTransferOwnerModal(updatedTransferOwnerModal)
  }

  const permissionSettingsSaveBtnClickHandler = () => {
    service.put(
      'parsers/' + parserId + '/',
      parser,
      (response) => {
        //router.replace(router.asPath)
        setUpdatedParser(!updatedParser)
      },
      (errorResponse) => {
        if (errorResponse.response.status == 403) {
          setPermissionSettingsErrorMessage('Permission Denied.')
        }
      }
    )
  }

  const parserSaveBtnClickHandler = () => {
    service.put(
      'parsers/' + parserId + '/',
      parser,
      (response) => {
        setUpdatedParser(!updatedParser)
      },
      (errorResponse) => {
        if (errorResponse.response.status == 403) {
          setParserErrorMessage('Permission Denied.')
        }
      }
    )
  }

  const exportBtnClickHandler = () => {
    service.get('parsers/' + parserId + '/export/', (response) => {
      const jsonString = `data:text/json;chatset=utf-8,${encodeURIComponent(
        JSON.stringify(response.data)
      )}`

      const link = document.createElement('a')
      link.href = jsonString
      link.download = 'parser-' + parserId + '.json'

      link.click()
    })
  }

  const chatbotTypeChangeHandler = (e) => {
    let updatedChatBot = { ...parser.chatbot }
    updatedChatBot.chatbotType = e.value
    setParser({
      ...parser,
      chatbot: updatedChatBot,
    })
  }

  const chatbotOpenAIResourceNameChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiResourceName = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot,
    })
  }

  const chatbotOpenAIApiKeyChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiApiKey = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot,
    })
  }

  const chatbotOpenAIDeploymentChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiDeployment = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot,
    })
  }

  const chatbotOpenAIDefaultQuestionChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiDefaultQuestion = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot,
    })
  }

  const chatbotBaseUrlChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.baseUrl = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot,
    })
  }

  const openAIEnabledChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.enabled = e.target.checked
    setParser({
      ...parser,
      openAi: updatedOpenAi,
    })
  }

  const openAIResourceNameChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiResourceName = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi,
    })
  }

  const openAIApiKeyChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiApiKey = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi,
    })
  }

  const openAIDeploymentChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiDeployment = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi,
    })
  }

  const openAIMetricsTenantIdChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsTenantId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey,
    })
  }

  const openAIMetricsClientIdChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsClientId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey,
    })
  }

  const openAIMetricsClientSecretChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsClientSecret = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey,
    })
  }

  const openAIMetricsSubscriptionIdChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsSubscriptionId = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey,
    })
  }

  const openAIMetricsServiceNameChangeHandler = (e) => {
    let updatedOpenAiMetricsKey = { ...parser.openAiMetricsKey }
    updatedOpenAiMetricsKey.openAiMetricsServiceName = e.target.value
    setParser({
      ...parser,
      openAiMetricsKey: updatedOpenAiMetricsKey,
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
    service.put(
      'parsers/' + parserId + '/',
      parser,
      (response) => {
        //router.replace(router.asPath)
        setUpdatedParser(!updatedParser)
      },
      (errorResponse) => {
        if (errorResponse.response.status == 403) {
        }
      }
    )
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  useEffect(() => {
    if (!router.isReady) return
    getGroups()
    getAccount()
  }, [router.isReady])

  useEffect(() => {
    if (!router.isReady) return
    getUsers()
  }, [router.isReady, account])

  const { parserId } = router.query

  return (
    <AdminLayout key={updatedParser}>
      <div className={styles.settingsWrapper}>
        <h1>Settings</h1>
        {parser && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Parser Name</Card.Title>
              <Form.Group className="mb-3" controlId="formParserName">
                <Form.Control
                  onChange={parserNameChangeHandler}
                  value={parser.name}
                />
              </Form.Group>
              {parserErrorMessage && parserErrorMessage != '' && (
                <p style={{ color: 'red' }}>{parserErrorMessage}</p>
              )}
              <Button variant="primary" onClick={parserSaveBtnClickHandler}>
                Save
              </Button>
            </Card.Body>
          </Card>
        )}
        {parser && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Parser Settings</Card.Title>
              <Form.Group className="mb-3" controlId="formAssumedTextWidth">
                <Form.Label>
                  PDF to image DPI (Smaller means smaller file size, larger
                  means higher image quality and higher OCR accuracy)
                </Form.Label>
                <RangeSlider
                  min={100}
                  max={300}
                  step={50}
                  value={parser.pdfToImageDpi}
                  onChange={pdfToImageDpiChangeHandler}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formAssumedTextWidth">
                <Form.Label>Assumed Text Width</Form.Label>
                <RangeSlider
                  min={0.1}
                  max={1.0}
                  step={0.05}
                  value={parser.assumedTextWidth}
                  onChange={assumedTextWidthChangeHandler}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formAssumedTextHeight">
                <Form.Label>Assumed Text Height</Form.Label>
                <RangeSlider
                  min={0.1}
                  max={1.0}
                  step={0.05}
                  value={parser.assumedTextHeight}
                  onChange={assumedTextHeightChangeHandler}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formSameLineAcceptanceRange"
              >
                <Form.Label>Same Line Acceptance Range</Form.Label>
                <RangeSlider
                  min={0.1}
                  max={1.0}
                  step={0.05}
                  value={parser.sameLineAcceptanceRange}
                  onChange={sameLineAcceptanceRangeChangeHandler}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formSameColumnAcceptanceRange"
              >
                <Form.Label>Same Column Acceptance Range</Form.Label>
                <RangeSlider
                  min={0.1}
                  max={1.0}
                  step={0.05}
                  value={parser.sameColumnAcceptanceRange}
                  onChange={sameColumnAcceptanceRangeChangeHandler}
                />
              </Form.Group>
              {parserErrorMessage && parserErrorMessage != '' && (
                <p style={{ color: 'red' }}>{parserErrorMessage}</p>
              )}
              <Button variant="primary" onClick={parserSaveBtnClickHandler}>
                Save
              </Button>
            </Card.Body>
          </Card>
        )}
        {parser && users && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Permissions</Card.Title>
              <Form.Group className="mb-3" controlId="formAssumedTextWidth">
                <Form.Label>Owner</Form.Label>
                <Select
                  options={users}
                  value={users.find((oo) => oo.value == parser.owner)}
                  onChange={(e) => ownerChangeHandler(e)}
                  menuPlacement="auto"
                  menuPosition="fixed"
                  isDisabled={true}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formAssumedTextHeight">
                <Form.Label>Permitted groups to manage this parser</Form.Label>
                <Select
                  options={groups}
                  value={groups.filter((oo) =>
                    parser.permittedGroups.map((u) => u).includes(oo.value)
                  )}
                  onChange={permittedGroupsChangeHandler}
                  isMulti
                  menuPlacement="auto"
                  menuPosition="fixed"
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formAssumedTextWidth">
                <Form.Label>Permitted users to manage this parser</Form.Label>
                <Select
                  options={users}
                  value={users.filter((oo) =>
                    parser.permittedUsers.map((u) => u).includes(oo.value)
                  )}
                  onChange={permittedUsersChangeHandler}
                  isMulti
                  menuPlacement="auto"
                  menuPosition="fixed"
                />
              </Form.Group>
              {permissionSettingsErrorMessage &&
                permissionSettingsErrorMessage != '' && (
                  <p style={{ color: 'red' }}>
                    {permissionSettingsErrorMessage}
                  </p>
                )}
              <Button
                variant="primary"
                onClick={permissionSettingsSaveBtnClickHandler}
              >
                Save
              </Button>
              {parser && account && parser.owner == account.id && (
                <>
                  <Button
                    variant="primary"
                    style={{ marginLeft: 10 }}
                    onClick={openTransferOwnerModalHandler}
                  >
                    Transfer Owner
                  </Button>
                  <Modal
                    show={transferOwnerModal.show}
                    onHide={closeTransferOwnerModalHandler}
                  >
                    <Modal.Header closeButton>
                      <Modal.Title>Transfer Owner</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                      <p>Are you sure to continue?</p>
                      <Select
                        options={users.filter((u) => u.value != account.id)}
                        value={users.find(
                          (oo) => oo.value == transferOwnerModal.ownerId
                        )}
                        onChange={(e) => transferOwnerChangeHandler(e)}
                        menuPlacement="auto"
                        menuPosition="fixed"
                      />
                    </Modal.Body>
                    <Modal.Footer>
                      <Button
                        variant="primary"
                        onClick={confirmTransferOwnerBtnClickHandler}
                      >
                        Transfer Owner
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={closeTransferOwnerModalHandler}
                      >
                        Close
                      </Button>
                    </Modal.Footer>
                  </Modal>
                </>
              )}
            </Card.Body>
          </Card>
        )}
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body>
            <Card.Title>Export</Card.Title>
            <Card.Text>
              Export and Import this parser to transfer between servers
            </Card.Text>
            <Button
              variant="primary"
              style={{ marginRight: 10 }}
              onClick={exportBtnClickHandler}
            >
              Export
            </Button>
          </Card.Body>
        </Card>
        {parser && parser.chatbot != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Chat Bot</Card.Title>
              <Form.Group className="mb-3" controlId="formChatBotType">
                <Select
                  options={chatBotOptions}
                  value={chatBotOptions.find(
                    (oo) => oo.value == parser.chatbot.chatbotType
                  )}
                  onChange={(e) => chatbotTypeChangeHandler(e)}
                  menuPlacement="auto"
                  menuPosition="fixed"
                />
              </Form.Group>
              {parser.chatbot.chatbotType == 'OPEN_AI' && (
                <>
                  <Form.Group
                    className="mb-3"
                    controlId="formChatbotOpenAIResourceName"
                  >
                    <Form.Label>Open AI Resource Name</Form.Label>
                    <Form.Control
                      onChange={chatbotOpenAIResourceNameChangeHandler}
                      value={parser.chatbot.openAiResourceName}
                    />
                  </Form.Group>
                  <Form.Group
                    className="mb-3"
                    controlId="formChatbotOpenAIApiKey"
                  >
                    <Form.Label>Open AI API KEY</Form.Label>
                    <Form.Control
                      onChange={chatbotOpenAIApiKeyChangeHandler}
                      value={parser.chatbot.openAiApiKey}
                    />
                  </Form.Group>
                  <Form.Group
                    className="mb-3"
                    controlId="formChatbotOpenAIDeployment"
                  >
                    <Form.Label>Open AI Deployment</Form.Label>
                    <Form.Control
                      onChange={chatbotOpenAIDeploymentChangeHandler}
                      value={parser.chatbot.openAiDeployment}
                    />
                  </Form.Group>
                  <Form.Group
                    className="mb-3"
                    controlId="formChatbotOpenAIDefaultQuestion"
                  >
                    <Form.Label>Open AI Default Question</Form.Label>
                    <Form.Control
                      onChange={chatbotOpenAIDefaultQuestionChangeHandler}
                      value={parser.chatbot.openAiDefaultQuestion}
                    />
                  </Form.Group>
                </>
              )}
              {parser.chatbot.chatbotType == 'ON_PREMISE_AI' && (
                <>
                  <Form.Group className="mb-3" controlId="formChatbotBaseUrl">
                    <Form.Label>Base Url</Form.Label>
                    <Form.Control
                      onChange={chatbotBaseUrlChangeHandler}
                      value={parser.chatbot.baseUrl}
                    />
                  </Form.Group>
                </>
              )}
              <Button variant="primary" onClick={chatBotSaveBtnClickHandler}>
                Save
              </Button>
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
                <Form.Control
                  onChange={openAIResourceNameChangeHandler}
                  value={parser.openAi.openAiResourceName}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIApiKey">
                <Form.Label>Open AI API KEY</Form.Label>
                <Form.Control
                  onChange={openAIApiKeyChangeHandler}
                  value={parser.openAi.openAiApiKey}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIDeployment">
                <Form.Label>Open AI Deployment</Form.Label>
                <Form.Control
                  onChange={openAIDeploymentChangeHandler}
                  value={parser.openAi.openAiDeployment}
                />
              </Form.Group>
              <Button variant="primary" onClick={openAISaveBtnClickHandler}>
                Save
              </Button>
            </Card.Body>
          </Card>
        )}
        {parser && parser.openAiMetricsKey && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Open AI Metrics</Card.Title>
              <Form.Group
                className="mb-3"
                controlId="formOpenAIMetricsKeyTenantId"
              >
                <Form.Label>Open AI Metrics Tenant ID</Form.Label>
                <Form.Control
                  onChange={openAIMetricsTenantIdChangeHandler}
                  value={parser.openAiMetricsKey.openAiMetricsTenantId}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formOpenAIMetricsKeyClientId"
              >
                <Form.Label>Open AI Metrics Client ID</Form.Label>
                <Form.Control
                  onChange={openAIMetricsClientIdChangeHandler}
                  value={parser.openAiMetricsKey.openAiMetricsClientId}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formOpenAIMetricsClientSecret"
              >
                <Form.Label>Open AI Metrics Client Secret</Form.Label>
                <Form.Control
                  onChange={openAIMetricsClientSecretChangeHandler}
                  value={parser.openAiMetricsKey.openAiMetricsClientSecret}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formOpenAIMetricsSubscriptionId"
              >
                <Form.Label>Open AI Metrics Subscription ID</Form.Label>
                <Form.Control
                  onChange={openAIMetricsSubscriptionIdChangeHandler}
                  value={parser.openAiMetricsKey.openAiMetricsSubscriptionId}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="formOpenAIMetricsServiceName"
              >
                <Form.Label>Open AI Metrics Service Name</Form.Label>
                <Form.Control
                  onChange={openAIMetricsServiceNameChangeHandler}
                  value={parser.openAiMetricsKey.openAiMetricsServiceName}
                />
              </Form.Group>
              <Button
                variant="primary"
                onClick={openAIMetricsSaveBtnClickHandler}
              >
                Save
              </Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </AdminLayout>
  )
}

export default Settings
