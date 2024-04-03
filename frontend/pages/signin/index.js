import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Form from 'react-bootstrap/Form'
import { Button } from 'react-bootstrap'

import CryptoJS from 'crypto-js'

import service from '../../service'

import OnePageLayout from '../../layouts/onePage'

import signInStyles from '../../styles/SignIn.module.css'

function SignIn() {
  const router = useRouter()

  const { callbackUrl } = router.query

  const [formValidation, setFormValidation] = useState({
    isValid: true,
    errorMessages: {
      email: '',
      password: '',
    },
  })

  const [formSuccessMessage, setFormSuccessMessage] = useState('')
  const [formErrorSummaryMessages, setFormErrorSummaryMessages] = useState('')

  const [signInForm, setSignInForm] = useState({
    email: '',
    password: '',
  })

  const emailChangeHandler = (e) => {
    setSignInForm(
      produce((draft) => {
        draft.email = e.target.value
      })
    )
  }

  const passwordChangeHandler = (e) => {
    setSignInForm(
      produce((draft) => {
        draft.password = e.target.value
      })
    )
  }

  const signInBtnClickHandler = (e) => {
    e.preventDefault()
    if (validateSignInForm()) {
      localStorage.removeItem('token')
      setFormErrorSummaryMessages('')
      service.post(
        'rest-auth/login/',
        {
          username: signInForm.email,
          email: signInForm.email,
          password: signInForm.password,
        },
        (response) => {
          if (response.status == 200) {
            localStorage.setItem('token', response.data.key)
            service.get('account/permissions', (permissionResponse) => {
              let ciphertextPermissions = CryptoJS.AES.encrypt(
                JSON.stringify(permissionResponse.data.permissions),
                'sonikgloballimited'
              ).toString()
              localStorage.setItem('permissions', ciphertextPermissions)
              if (callbackUrl) {
                router.push(callbackUrl)
              } else {
                router.push('/workbench/parsers')
              }
            })
          } else {
            setFormErrorSummaryMessages(
              'Cannot connect to the server. Please contact system administrator.'
            )
          }
        },
        (error) => {
          if (
            error.response &&
            error.response.data &&
            error.response.data.nonFieldErrors
          ) {
            setFormErrorSummaryMessages(error.response.data.nonFieldErrors[0])
          } else if (error.response && error.response.data) {
            setFormErrorSummaryMessages(error.response.data[0])
          } else {
            setFormErrorSummaryMessages(
              'Cannot connect to the server. Please contact system administrator.'
            )
            console.error(error)
          }
        }
      )
    }
  }

  const validateSignInForm = () => {
    let isValid = true
    let errorMessages = []

    let emailRegex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/

    if (signInForm.email.length <= 0) {
      errorMessages.email = "'Email' cannot be empty."
      isValid = false
    } else if (!emailRegex.test(signInForm.email)) {
      errorMessages.email = "'Email' format is not correct."
      isValid = false
    }
    if (signInForm.password.length <= 0) {
      errorMessages.password = "'Password' cannot be empty."
      isValid = false
    }
    setFormValidation({
      isValid,
      errorMessages,
    })
    return isValid
  }

  return (
    <>
      <Head>
        <title>Cashew - Sign In</title>
      </Head>
      <OnePageLayout>
        <div className={signInStyles.wrapper}>
          <div>
            <i
              className={signInStyles.backBtn + ' bi' + ' bi-arrow-left'}
              onClick={() => router.back()}
            ></i>
            <h1 className={signInStyles.h1}>Sign in</h1>
          </div>
          <div className={signInStyles.form}>
            <Form>
              <Row>
                <Form.Group
                  as={Col}
                  className={signInStyles.col + ' xs-12' + ' md-3'}
                  controlId="formEmail"
                >
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    placeholder="Enter email"
                    autoComplete="username"
                    onChange={(e) => emailChangeHandler(e)}
                    value={signInForm.email}
                  />
                  {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.email}
                    </div>
                  )}
                </Form.Group>
              </Row>
              <Row className="xs-12 md-3">
                <Form.Group
                  as={Col}
                  className={signInStyles.col + ' xs-12' + ' md-3'}
                  controlId="formPassword"
                >
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    placeholder="Enter password"
                    autoComplete="current-password"
                    onChange={(e) => passwordChangeHandler(e)}
                    value={signInForm.password}
                  />
                  {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.password}
                    </div>
                  )}
                </Form.Group>
              </Row>
              {formSuccessMessage && formSuccessMessage.length > 0 && (
                <Row>
                  <div className="formSuccessMessage">{formSuccessMessage}</div>
                </Row>
              )}
              <Row>
                {formErrorSummaryMessages && (
                  <div className="formErrorMessage">
                    {formErrorSummaryMessages}
                  </div>
                )}
              </Row>
              <Row>
                <Form.Group
                  as={Col}
                  className={
                    signInStyles.actions +
                    ' ' +
                    signInStyles.col +
                    ' xs-12' +
                    ' md-3'
                  }
                >
                  <Button
                    type="submit"
                    className={signInStyles.signInBtn + ' ' + signInStyles.btn}
                    onClick={(e) => signInBtnClickHandler(e)}
                  >
                    Sign in
                  </Button>
                  <Button
                    type="button"
                    className={
                      signInStyles.signUpBtn +
                      ' ' +
                      signInStyles.btn +
                      ' btn-secondary'
                    }
                    onClick={() => router.push('signup')}
                  >
                    Do not have account yet? Sign up now!
                  </Button>
                </Form.Group>
              </Row>
            </Form>
          </div>
        </div>
      </OnePageLayout>
    </>
  )
}

export default SignIn
