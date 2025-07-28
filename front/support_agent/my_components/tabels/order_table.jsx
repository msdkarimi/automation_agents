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
            <Table.Th ta="center">Item Name</Table.Th>
            <Table.Th ta="center">Customer ID</Table.Th>
            <Table.Th ta="center">Date</Table.Th>
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

  let badg_color = { from: 'gray', to: 'rgba(28, 27, 27, 0.88)', deg: 90 }

  if (props.element.order_status == 'confirmed')
    badg_color = { from: 'green', to: 'lime', deg: 196 }
  else if (props.element.order_status == 'failed')
    badg_color = { from: 'red', to: 'pink', deg: 90 }
  else if ( props.element.order_status ==  'canceled')
    badg_color = { from: 'pink', to: 'violet', deg: 90 }

  
  return (
    <>
      <Table.Tr>
        <Table.Td>{props.element.item.item_name}</Table.Td>
        <Table.Td>{props.element.customer.customer_id}</Table.Td>
        <Table.Td>{props.element.order_date}</Table.Td>
        <Table.Td>  <Badge variant="gradient" gradient={badg_color}>{props.element.order_status}</Badge></Table.Td>
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
          <ModalContent agent_response={props.agent_response} selection={props.selection}/>
        )}
      </Modal>
    </>
  );
}

function ModalContent(props){
  const { ref, width, height } = useElementSize();

  console.log(props.selection.status)

  return(
    <SimpleGrid cols={1} spacing="xs">
              <div>
                <p><strong>Customer ID:</strong> <Pill color="cyan">{props.selection.customer_id}</Pill></p>
              </div>
              <div>
                <p><strong>Date:</strong> <Pill color="cyan">{props.selection.date_received}</Pill> </p>
              </div>
              <div >
              <Group align="center" spacing="sm">
                <strong>Status:</strong> 
                
                <Select placeholder="Pick value" data={['Close','Open']} value={props.selection.status}/>
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