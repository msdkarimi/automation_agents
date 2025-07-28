import { Table, Button, Modal, Select, Divider, Group, SimpleGrid, Badge, ActionIcon, Pill } from '@mantine/core';
import { IconCirclesRelation, IconRobot, IconAdjustments, IconDots } from '@tabler/icons-react';
import { useElementSize } from '@mantine/hooks';


export function MyTable(props) {
  const icon = <IconCirclesRelation />;



  


  return (
    
    <>
      <Table ta="center" stickyHeader>
        <Table.Thead bg="dark.9">
          <Table.Tr>
            <Table.Th ta="center">Subject</Table.Th>
            <Table.Th ta="center">Received</Table.Th>
            <Table.Th ta="center">Status</Table.Th>
            <Table.Th ta="center">Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {props.elements.map((element) => (
            <Row
              key={element.id}
              element={element}
              open={props.open}
              close={props.close}
              selection={props.selection}
              setSelection={props.setSelection}
              opened={props.opened}
              agent_response={props.agent_response}

            />
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
}

function Row(props) {
  return (
    <>
      <Table.Tr>
        <Table.Td>{props.element.subject}</Table.Td>
        <Table.Td>{props.element.date_received}</Table.Td>
        <Table.Td>{props.element.status=='close'? <Badge   variant="gradient" gradient={{ from: 'green', to: 'lime', deg: 196 }}>Close</Badge> : <Badge  variant="gradient" gradient={{ from: 'pink', to: 'red', deg: 90  }}>Open</Badge>  }</Table.Td>
        <Table.Td>
        <ActionIcon
            variant="light"
            color="gray"
            aria-label="Settings"
            onClick={() => {
              props.setSelection(props.element); // Set the selected element
              props.open(); // Open the modal
            }}
          >
          <IconDots style={{ width: '70%', height: '70%' }} stroke={1.5} />
        </ActionIcon>
        </Table.Td>
      </Table.Tr>

      <Modal
        opened={props.opened && props.selection?.id === props.element.id} // Only open for the selected row
        onClose={() => {
          props.close();
          props.setSelection(null); // Clear selection on close
        }}
        title={props.element.subject}
        size="80%"
      >
        {props.selection && (
          <ModalContent agent_response={props.agent_response} selection={props.selection} setSelection={props.setSelection}/>
        )}
      </Modal>
    </>
  );
}

function ModalContent(props){
  const { ref, width, height } = useElementSize();

  let has_links = props.selection.ticket_links

  let order_id = null 
  let payment_id = null
  let purchase_id = null
  let sop_id = null

  if (has_links)
  {
    if(has_links.order_id)
      order_id = has_links.order_id

    if(has_links.payment_id)
      payment_id = has_links.payment_id

    if(has_links.purchase_id)
      purchase_id = has_links.purchase_id

    if(has_links.sop_id)
      sop_id = has_links.sop_id
  }


  return(
    <SimpleGrid cols={1} spacing="xs">
              <div>
                <p><strong>Customer ID:</strong> <Pill color="cyan">{props.selection.customer_id}</Pill></p>
                <p><strong>Date:</strong> <Pill color="cyan">{props.selection.date_received}</Pill> </p>

                {order_id ? <p><strong>Order ID:</strong> <Pill color="cyan">{order_id}</Pill></p> :<></>}
                {payment_id ? <p><strong>Payment ID:</strong> <Pill color="cyan">{payment_id}</Pill></p> :<></>}
                {purchase_id ? <p><strong>Purchase ID:</strong> <Pill color="cyan">{purchase_id}</Pill></p> :<></>}
                {sop_id ? <p><strong>Sop. ID:</strong> <Pill color="cyan">{sop_id}</Pill></p> :<></>}
              </div>
              <div >
              <Group align="center" spacing="sm">
                <strong>Status:</strong> 
                
                <Select placeholder="Pick value" data={['close','open']} value={props.selection.status}
                
                onChange={(new_value)=>{
                  if (new_value != null){
                  props.setSelection((old_state)=>
                    ({...old_state, status:new_value})
                  )
                }

                }}
                />
                
              </Group>
              </div>
              <div>
                <textarea readOnly value={props.selection.customer_comment || ''} className='my_text_area' ref={ref} />
              </div>
              
              <div>

              <textarea ref={ref} className='my_text_area' />
                {/* <Textarea
                  description="Your Response:"
                  placeholder="Type Your Response Here"
                  // value={props.agent_response}
                /> */}
              </div>

              <Group gap="xs">
                <Button leftSection={<IconRobot size={18} />} variant="light" color="orange">Draft Reply Agent</Button> <Button variant="outline" color="lime">Reply</Button>
              </Group>
            
            <div>
              <Divider my="md" variant="dashed"/>
            </div>
  
            <Group justify="flex-end" gap="xs">
          <Button leftSection={<IconRobot size={18} />} variant="filled" color="violet">Invoke Case Contex Agent</Button> <Button leftSection={<IconRobot size={18} />} variant="filled" color="pink">Invoke Standard Operating Procedure Agent</Button>
        </Group>
        </SimpleGrid>

  );
}