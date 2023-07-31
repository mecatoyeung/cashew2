import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'
import Head from 'next/head'

import { produce } from "immer"

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Form from 'react-bootstrap/Form'
import { Button } from 'react-bootstrap'

import Select from 'react-select'

import service from '../../service'

import OnePageLayout from '../../layouts/onePage'

import activateEmailStyles from "../../styles/ActivateEmail.module.css"

export default function ActivateEmail() {

  const router = useRouter()

  const { token } = router.query

  const [hasActivated, setHasActivated] = useState(false)

  const [isActivateSuccess, setIsActivateSuccess] = useState(false)

  const activateEmail = () => {
    console.log(token)
    service.post("/rest-auth/registration/verify-email/", {
      key: token
    }, response => {
      setHasActivated(true)
      setIsActivateSuccess(true)
    }, error => {
      console.error(error)
    })
  }

  useEffect(() => {
    activateEmail()
  }, [token])

  return (
    <>
      <Head>
        <title>Cashew - Activate Email</title>
      </Head>
      <OnePageLayout>
        <div className={activateEmailStyles.wrapper}>
          <div>
            <h1 className={activateEmailStyles.h1}>
              Activate Email
            </h1>
          </div>
          <div className={activateEmailStyles.form}>
            <Form>
              <Row>
                <Form.Group as={Col} className={activateEmailStyles.col + " xs-12" + " md-3"}>
                  <Form.Label>
                    {!hasActivated && "Please wait..."}
                    {hasActivated && isActivateSuccess && "Your email has been activated!"}
                    {hasActivated && !isActivateSuccess && "Activation failed"}
                  </Form.Label>
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={activateEmailStyles.actions + " " + activateEmailStyles.col + " xs-12" + " md-3"}>
                  <Button type="button" className={activateEmailStyles.signInBtn + " " + activateEmailStyles.btn} onClick={() => router.push("/signin")}>Sign In Now!</Button>
                  <Button type="button" className={activateEmailStyles.homeBtn + " " + activateEmailStyles.btn + " btn-secondary"} onClick={() => router.push("/")}>Home</Button>
                </Form.Group>
              </Row>
            </Form>
          </div>
        </div>
      </OnePageLayout>
    </>
  )
}
